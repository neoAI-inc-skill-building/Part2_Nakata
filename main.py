import os
os.environ["NEOLLM_LOGGER_LEVEL"] = "DEBUG"
from neollm import MyLLM
from neollm.types import Messages, Response
from custom_prompt_dict import EXTRACT_DEFINITION_DATA
from dotenv import load_dotenv
from custom_prompt_dict import Prompt
import re
import json
import csv
import pandas as pd
import datetime

class ExtractorLLM(MyLLM):  # type: ignore[misc]
    def _preprocess(self, inputs: dict[str, str]) -> Messages:
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
    
    def json2dict(self, json_string: str) -> dict[any, any] | str:
        """
        JSON文字列をPython dictに変換する

        Args:
            json_string (str): 変換するJSON文字列

        Returns:
            dict: 変換されたPython dict
        """
        try:
            match = re.search(r"\{.*\}", json_string, re.DOTALL)
            if match:
                json_string = match.group(0)
            json_string = json_string.replace("'", '"')
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"JSONデコードエラーが発生しました：{e}")
            return json_string
        
    def _clean_field_value(self, value):  # ← selfを追加してクラス内に置く
        if isinstance(value, str):
            value = value.strip('"')
            value = value.replace(',', '')
        return value

    def _postprocess(self, response):
        result = response.choices[0].message.content
        result_dict = self.json2dict(result)
        cleaned_result_dict = {k: self._clean_field_value(v) for k, v in result_dict.items()}
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
    for key, value in definition_data.items():
        result[value.japanese_name] = value.prompt
    return result

if __name__ == "__main__":
    now = datetime.datetime.now()
    strdt = now.strftime("%Y-%m-%d-%H-%M")

    load_dotenv()

    # onb_filename.csvからファイル名一覧を読み込む
    filenames_df = pd.read_csv("onb_filename.csv")

    # 抽出モードの選択
    mode = input("抽出モードを選択してください（1: 全帳票 / 2: 1帳票のみ）: ")
    if mode == "2":
        target_filename = input("抽出するファイル名を入力してください（例: receipt_727.png）: ")
        filenames = [target_filename]
    else:
        filenames = list(filenames_df["ファイル名"])

    output_format = make_output_format(EXTRACT_DEFINITION_DATA)

    # ヘッダーの作成とCSVの初期化（ループ前に1回だけ）
    headers = ["ファイル名"] + [value.japanese_name for value in EXTRACT_DEFINITION_DATA.values()]
    with open(f"onb_extraction_results/{strdt}_extraction_result.csv", "w", newline="", encoding="utf-8") as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=headers)
        writer.writeheader()
    
    # 全帳票をループで処理
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

        # OCRテキストの読み込み
        with open(ocr_path, "r", encoding="utf-8") as f:
            ocr_text = f.read()

        # LLMで情報抽出
        output = exllm(inputs={"output_format": output_format, "ocr_text": ocr_text})

        # CSVに追記
        with open(f"onb_extraction_results/{strdt}_extraction_result.csv", "a", newline="", encoding="utf-8") as out_csv:
            writer = csv.DictWriter(out_csv, fieldnames=headers)
            output["ファイル名"] = filename
            writer.writerow(output)