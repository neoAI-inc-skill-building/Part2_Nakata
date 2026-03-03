import os

os.environ["NEOLLM_LOGGER_LEVEL"] = "DEBUG"
import csv
import datetime
import json
import logging
import re
from typing import Any, TypedDict, cast

from dotenv import load_dotenv
from neollm import MyLLM
from neollm.types import Messages, Response
import pandas as pd

from custom_prompt_dict import EXTRACT_DEFINITION_DATA, Prompt

logger = logging.getLogger(__name__)


class ExtractorInputs(TypedDict):
    output_format: dict[str, str]
    ocr_text: str


class ExtractorLLM(MyLLM):  # type: ignore[misc]
    def _preprocess(self, inputs: ExtractorInputs) -> Messages:
        system_prompt = (
            "帳票の<OCR_TEXT>をもとに、<OUTPUT FORMAT>に従って情報を抽出してください。\n"
            "抽出ができなかった場合は、'-'と出力してください。\n"
        )
        user_prompt = f"<OUTPUT_FORMAT>\n {inputs['output_format']} \n\n<OCR_TEXT>\n```\n {inputs['ocr_text']} \n```"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return messages

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
            parsed = json.loads(extracted)
        except json.JSONDecodeError:
            logger.exception("JSONデコードエラーが発生しました")
            raise

        if not isinstance(parsed, dict):
            msg = "JSONのトップレベルがオブジェクトではありませんでした"
            raise TypeError(msg)

        return cast("dict[str, Any]", parsed)

    def _clean_field_value(self, field_value: str) -> str:
        return field_value.replace(",", "").strip('"')

    def _postprocess(self, response: Response) -> dict[str, str]:
        content = response.choices[0].message.content
        if not isinstance(content, str):
            msg = "LLMの応答contentが文字列ではありませんでした"
            raise TypeError(msg)

        result_dict = self.json2dict(content)
        cleaned_result_dict: dict[str, str] = {}
        for key, value in result_dict.items():
            cleaned_result_dict[str(key)] = self._clean_field_value(str(value))
        return cleaned_result_dict


def make_output_format(definition_data: dict[str, Prompt]) -> dict[str, str]:
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
    if mode == "2":
        target_filename = input("抽出するファイル名を入力してください（例: receipt_727.png）: ")
        filenames = [target_filename]
    else:
        filenames = list[Any](filenames_df["ファイル名"])

    output_format = make_output_format(EXTRACT_DEFINITION_DATA)

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
                "max_tokens": 1024,
            },
        )

        ocr_path = f"onb_ocr/av_{filename}.txt"

        with open(ocr_path, encoding="utf-8") as f:
            ocr_text = f.read()

        output = exllm(inputs={"output_format": output_format, "ocr_text": ocr_text})

        with open(
            f"onb_extraction_results/{strdt}_extraction_result.csv", "a", newline="", encoding="utf-8"
        ) as out_csv:
            writer = csv.DictWriter(out_csv, fieldnames=headers)
            output["ファイル名"] = filename
            writer.writerow(output)
