from abc import abstractmethod

from dotenv import load_dotenv
from neollm import MyLLM
from neollm.types import Messages, Response
from custom_prompt_dict import EXTRACT_DEFINITION_DATA


class ExtractorLLM(MyLLM):  # type: ignore[misc]
    def _preprocess(self, inputs: dict[str, str]) -> Messages:
        system_prompt = (
            "帳票の<OCR_TEXT>をもとに、<OUTPUT FORMAT>に従って情報を抽出してください。\n"
            "抽出ができなかった場合は、'-'と出力してください。\n"
        )
        user_prompt = "<OUTPUT_FORMAT>\n [output_format] \n\n<OCR_TEXT>\n```\n [ocr_text] \n```"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return messages

    def _postprocess(self, response: Response) -> str:
        return response.choices[0].message.content  # type: ignore[no-any-return]


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

    output = exllm(inputs={"output_format": make_output_format(EXTRACT_DEFINITION_DATA)})
    print(output)