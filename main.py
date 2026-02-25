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

    def _postprocess(self, response: Response) -> str:
        result = response.choices[0].message.content  # type: ignore[no-any-return]
        return self.json2dict(result)


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
    # .envの読み込み
    load_dotenv()
    
    # 抽出Classの初期化
    exllm = ExtractorLLM(
        platform="openai",
        model="gpt-4o-mini",
        verbose=True,  # inputsやoutputsを出力するかどうか。Falseの場合、出力されない。
        llm_settings={
            "temperature": 0,
            "max_tokens": 1024,
        },  # temperatureは、値が小さいほど一貫性のある出力で、大きいほど多様な出力となる。
    )

    with open("onb_ocr/av_receipt_727.png.txt", "r", encoding="utf-8") as f:
        ocr_text = f.read()

    output = exllm(inputs={"output_format": make_output_format(EXTRACT_DEFINITION_DATA), "ocr_text": ocr_text})
    

    # headersの作成(EXTRACT_DEFINITION_DATAのjapanese_nameから作成しよう。）
    headers = ["ファイル名"] + [value.japanese_name for value in EXTRACT_DEFINITION_DATA.values()]

    with open("onb_extraction_results/extraction_result.csv", "w", newline="", encoding="utf-8") as out_csv:
    # DictWriterの作成（fieldnamesをheadersに設定）
        writer = csv.DictWriter(out_csv, fieldnames=headers)
    # ヘッダー行の書き込み
        writer.writeheader()
    # データ行の書き込み
        output["ファイル名"] = "av_receipt_727.png.txt"
        writer.writerow(output)