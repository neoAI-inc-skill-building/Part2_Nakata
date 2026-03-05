import os

os.environ["NEOLLM_LOGGER_LEVEL"] = "DEBUG"
import csv
import datetime
import json
import logging
import re
from typing import Any

from dotenv import load_dotenv
from neollm import MyLLM
from neollm.types import Messages, Response
import pandas as pd
from pydantic import BaseModel, StrictStr

from custom_prompt_dict import EXTRACT_DEFINITION_DATA, Prompt

logger = logging.getLogger(__name__)


class ExtractorInputs(BaseModel):
    extract_definition_data: dict[StrictStr, Prompt]
    ocr_text: StrictStr


class ExtractorLLM(MyLLM):  # type: ignore[misc]
    def _preprocess(self, inputs: ExtractorInputs) -> Messages:
        system_prompt = (
            "帳票の<OCR_TEXT>をもとに、<OUTPUT_FORMAT>に従って情報を抽出してください。\n"
            "抽出ができなかった場合は、'-'と出力してください。\n"
        )

        output_format = self._make_output_format(inputs.extract_definition_data)

        cot_items_list = [
            "受領会社",
            "発行会社",
            "受領会社電話番号",
            "受領会社郵便番号",
            "受領会社住所",
            "発行会社電話番号",
            "発行会社郵便番号",
            "発行会社住所",
        ]

        extracted_cot_japanese_items_list = [item for item in output_format if item in cot_items_list]

        if extracted_cot_japanese_items_list:
            cot_system_prompt = (
                f"\n以下の項目は推論が必要です：{extracted_cot_japanese_items_list}\n"
                "【手順】\n"
                "1. まず「---思考---」と書き、帳票内の「御中」「様」などの敬称から受領会社を特定し、"
                "それ以外の会社を発行会社として特定する。それぞれの住所・郵便番号・電話番号を確認する。\n"
                "2. 次に「---結果---」と書き、全ての項目を含むJSONオブジェクトのみを出力する。\n"
                "\n【重要】\n"
                '- 金額は必ずカンマなし・円記号なしの整数文字列で出力すること（例: "8734"）。小数点はつけないこと。\n'
                "- 結果のJSONには思考内容を含めず、抽出結果のみを記載すること。\n"
            )
            system_prompt += cot_system_prompt

        user_prompt = f"<OUTPUT_FORMAT>\n{output_format}\n\n<OCR_TEXT>\n```\n{inputs.ocr_text}\n```"
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def json2dict(self, json_string: str) -> dict[str, Any]:
        """
        JSON文字列をPython dictに変換する

        Args:
            json_string (str): 変換するJSON文字列

        Returns:
            dict: 変換されたPython dict
        """
        match = re.search(r"\{.*\}", json_string, re.DOTALL)
        if match is None:
            msg = "JSONオブジェクト（{...}）が見つかりませんでした"
            raise ValueError(msg)

        extracted = match.group(0).replace("'", '"')
        try:
            parsed: dict[str, Any] = json.loads(extracted)
        except json.JSONDecodeError:
            logger.exception("JSONデコードエラーが発生しました")
            raise

        return parsed

    def _postprocess(self, response: Response) -> dict[str, str]:
        content = response.choices[0].message.content
        if not isinstance(content, str):
            msg = "LLMの応答contentが文字列ではありませんでした"
            raise TypeError(msg)

        result_dict = self.json2dict(content)
        return {key: str(value).replace(",", "").strip('"') for key, value in result_dict.items()}

    def _make_output_format(self, definition_data: dict[str, Prompt]) -> dict[str, str]:
        """
        EXTRACT_DEFINITION_DATAを、key:japanese_name, value: promptとした辞書に変換する関数

        Args:
            dict[str, Prompt]:
                # keyが任意の文字列、valueがPromptクラスの辞書。以下例。
                {
                    "recipient_company": Prompt(
                        prompt="抽出結果を出力せよ",
                        japanese_name="受領会社"
                    )
                }

        Returns:
            dict[str, str]:
                # keyがjapanese_name、valueがpromptの辞書,以下例。
                {
                    "受領会社": "抽出結果を出力せよ"
                }
        """
        result = {}
        for value in definition_data.values():
            result[value.japanese_name] = value.prompt
        return result


if __name__ == "__main__":
    now = datetime.datetime.now(datetime.timezone.utc)
    strdt = now.strftime("%Y-%m-%d-%H-%M")

    load_dotenv()

    filenames_df = pd.read_csv("onb_filename.csv")

    mode = input("抽出モードを選択してください（1: 全帳票 / 2: 1帳票のみ）: ")
    filenames: list[str]
    if mode == "2":
        filenames = [input("抽出するファイル名を入力してください（例: receipt_727.png）: ")]
    else:
        filenames = filenames_df["ファイル名"].tolist()

    headers = ["ファイル名"] + [value.japanese_name for value in EXTRACT_DEFINITION_DATA.values()]
    with open(f"onb_extraction_results/{strdt}_extraction_result.csv", "w", newline="", encoding="utf-8") as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=headers)
        writer.writeheader()

    for filename in filenames:
        exllm = ExtractorLLM(
            platform="openai",
            model="gpt-4o-mini",
            verbose=True,
            llm_settings={
                "temperature": 0,
                "max_tokens": 4096,
            },
        )

        with open(f"onb_ocr/av_{filename}.txt", encoding="utf-8") as f:
            ocr_text = f.read()

        output = exllm(inputs={"extract_definition_data": EXTRACT_DEFINITION_DATA, "ocr_text": ocr_text})

        with open(
            f"onb_extraction_results/{strdt}_extraction_result.csv", "a", newline="", encoding="utf-8"
        ) as out_csv:
            writer = csv.DictWriter(out_csv, fieldnames=headers)
            output["ファイル名"] = filename
            writer.writerow(output)
