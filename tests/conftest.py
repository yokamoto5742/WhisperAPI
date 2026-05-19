import os

# app.py のモジュールレベルで Groq クライアントが初期化される前にキーを設定する
os.environ.setdefault("GROQ_API_KEY", "test-key-for-pytest")
