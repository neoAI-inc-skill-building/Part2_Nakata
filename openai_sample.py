from dotenv import load_dotenv
from neollm import MyLLM
from neollm.types import Messages, Response

load_dotenv()


class SampleMyLLM(MyLLM):  # type: ignore[misc]
    def _preprocess(self, inputs: str) -> Messages:
        return [
            {"role": "system", "content": "You are neoAI."},
            {"role": "user", "content": inputs},
        ]

    def _postprocess(self, response: Response) -> str:
        content = response.choices[0].message.content
        if not isinstance(content, str):
            msg = "LLMの応答contentが文字列ではありませんでした"
            raise TypeError(msg)
        return content


sample_myllm = SampleMyLLM(
    platform="openai",
    model="gpt-4o-2024-08-06",  # デプロイしたmodel_nameから選ぶ
)
sample_myllm("あなたの名前は？")
