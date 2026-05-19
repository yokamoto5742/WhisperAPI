---
name: verify
description: pyrightによる型チェックとpytestによるテストをまとめて実行する。コード変更後の検証に使用する。
---

以下の順序で実行し、それぞれの結果を報告する:

1. **型チェック** (pyright):
   ```
   python -m pyright
   ```

2. **テスト** (pytest with coverage):
   ```
   python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
   ```

エラーがあれば内容を要約し、修正が必要な箇所を特定する。
両方パスしたら「型チェック・テストともにパス」と報告する。
