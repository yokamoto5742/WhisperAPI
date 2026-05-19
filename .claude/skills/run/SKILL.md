---
name: run
description: Streamlitアプリを起動する。ユーザーが /run と入力したとき、またはアプリを起動したいときに使用する。
disable-model-invocation: true
---

以下のコマンドでStreamlitアプリを起動する:

```
streamlit run app.py
```

起動前に `.env` ファイルに `GROQ_API_KEY` が設定されているか確認する。
設定がない場合はユーザーに通知する。
