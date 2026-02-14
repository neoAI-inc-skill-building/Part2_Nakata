import os

from dotenv import load_dotenv
import openai

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# APIリクエストの実行
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "あなたは親切なアシスタントです。"},
        {"role": "user", "content": "こんにちは"},
    ],
)

# 応答の取得
print(response.choices[0].message.content)
