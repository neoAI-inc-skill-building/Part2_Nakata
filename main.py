from abc import abstractmethod

from dotenv import load_dotenv
from neollm import MyLLM
from neollm.types import Messages, Response


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

    output = exllm(inputs={})
