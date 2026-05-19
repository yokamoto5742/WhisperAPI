# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Streamlit + Groq Whisper API による音声文字起こしアプリ（日本語出力専用）。

- 起動: `streamlit run app.py`
- 必須環境変数: `GROQ_API_KEY`（`.env` ファイルで管理）
- 対応フォーマット: mp3, mp4, webm, wav, mpeg, mpga, m4a
- ファイルサイズ上限: 25MB
- 使用モデル: `whisper-large-v3`（言語: 日本語固定）

## アーキテクチャ

```
app.py          # Streamlitエントリポイント（UIロジックは最小限）
app/            # StreamlitのUIコンポーネント
service/        # ビジネスロジック（Groq API呼び出し、音声処理）
utils/          # 設定管理（config.ini）・環境変数読み込み（.env）
```

`service/` と `app/` はまだ空のスタブ。新機能は適切なレイヤーに配置する。

## テスト

テストはまだ存在しない。`pytest-test-creator` エージェントを使用して作成する。

@.claude/rules/testing.md

## コーディング規約

@.claude/rules/coding-guidelines.md
@.claude/rules/python-coding.md
@.claude/rules/response-style.md

## コミット規約

@.claude/rules/commit.md
