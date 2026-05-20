import configparser
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.components import load_markdown_file
from external_service.groq_api import transcribe_audio


class TestLoadMarkdownFile:
    def test_returns_file_contents(self, tmp_path: Path) -> None:
        """ファイルが存在する場合、その内容を文字列で返すこと"""
        md_file = tmp_path / "test.md"
        md_file.write_text("# テスト\n内容", encoding="utf-8")

        result = load_markdown_file(str(md_file))

        assert result == "# テスト\n内容"

    def test_raises_when_file_not_found(self, tmp_path: Path) -> None:
        """存在しないファイルを指定した場合 FileNotFoundError が送出されること"""
        with pytest.raises(FileNotFoundError):
            load_markdown_file(str(tmp_path / "nonexistent.md"))

    def test_returns_empty_string_for_empty_file(self, tmp_path: Path) -> None:
        """空ファイルの場合、空文字列を返すこと"""
        md_file = tmp_path / "empty.md"
        md_file.write_text("", encoding="utf-8")

        result = load_markdown_file(str(md_file))

        assert result == ""


class TestTranscribeAudio:
    def _make_temp_audio_file(
        self, tmp_path: Path, data: bytes = b"dummy_audio_data"
    ) -> str:
        """テスト用の擬似音声ファイルを作成してパスを返す"""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(data)
        return str(audio_file)

    def _make_config(
        self,
        model: str = "whisper-large-v3",
        language: str = "ja",
        prompt: str = "",
    ) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config["WHISPER"] = {
            "MODEL": model,
            "LANGUAGE": language,
            "PROMPT": prompt,
        }
        return config

    def test_returns_transcription_on_success(self, tmp_path: Path) -> None:
        """Groq API が成功した場合、文字起こし結果を返すこと"""
        audio_path = self._make_temp_audio_file(tmp_path)
        config = self._make_config()
        expected = "文字起こし結果のテキスト"

        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = expected

        result = transcribe_audio(audio_path, config, mock_client)

        assert result == expected

    def test_returns_none_on_exception(self, tmp_path: Path) -> None:
        """Groq API が例外を送出した場合、None を返すこと"""
        audio_path = self._make_temp_audio_file(tmp_path)
        config = self._make_config()

        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.side_effect = Exception("API エラー")

        result = transcribe_audio(audio_path, config, mock_client)

        assert result is None

    def test_returns_none_for_nonexistent_file(self) -> None:
        """存在しないファイルパスを指定した場合、None を返すこと"""
        config = self._make_config()
        mock_client = MagicMock()

        result = transcribe_audio("/nonexistent/path/audio.wav", config, mock_client)

        assert result is None

    def test_api_called_with_correct_params(self, tmp_path: Path) -> None:
        """Groq API が正しいパラメータで呼ばれること"""
        audio_path = self._make_temp_audio_file(tmp_path)
        config = self._make_config(
            model="whisper-large-v3",
            language="ja",
        )

        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = "結果"

        transcribe_audio(audio_path, config, mock_client)

        call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
        assert call_kwargs.get("model") == "whisper-large-v3"
        assert call_kwargs.get("language") == "ja"
        assert call_kwargs.get("response_format") == "text"
