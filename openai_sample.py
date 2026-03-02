from neollm import MyLLM
from dotenv import load_dotenv

from neollm.types import Messages, Response

load_dotenv()


class SampleMyLLM(MyLLM):
    def _preprocess(self, inputs: str) -> Messages:
        return [
            {"role": "system", "content": "You are neoAI."},
            {"role": "user", "content": inputs},
        ]

    def _postprocess(self, response: Response) -> str:
        return response.choices[0].message.content


sample_myllm = SampleMyLLM(
    platform="openai",
    model="gpt-4o-2024-08-06",  # デプロイしたmodel_nameから選ぶ
)
sample_myllm("あなたの名前は？")
