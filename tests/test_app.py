import importlib.util
import io
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# app/ パッケージより app.py を優先してロードする
_app_py = Path(__file__).parent.parent / "app.py"
_spec = importlib.util.spec_from_file_location("app_module", _app_py)
assert _spec is not None and _spec.loader is not None
app_module = importlib.util.module_from_spec(_spec)
sys.modules["app_module"] = app_module
_spec.loader.exec_module(app_module)  # type: ignore[attr-defined]


class TestLoadMarkdownFile:
    def test_returns_file_contents(self, tmp_path: Path) -> None:
        """ファイルが存在する場合、その内容を文字列で返すこと"""
        md_file = tmp_path / "test.md"
        md_file.write_text("# テスト\n内容", encoding="utf-8")

        result = app_module.load_markdown_file(str(md_file))

        assert result == "# テスト\n内容"

    def test_raises_when_file_not_found(self, tmp_path: Path) -> None:
        """存在しないファイルを指定した場合 FileNotFoundError が送出されること"""
        with pytest.raises(FileNotFoundError):
            app_module.load_markdown_file(str(tmp_path / "nonexistent.md"))

    def test_returns_empty_string_for_empty_file(self, tmp_path: Path) -> None:
        """空ファイルの場合、空文字列を返すこと"""
        md_file = tmp_path / "empty.md"
        md_file.write_text("", encoding="utf-8")

        result = app_module.load_markdown_file(str(md_file))

        assert result == ""


class TestTranscribeAudio:
    def _make_audio_file(self, data: bytes = b"dummy_audio_data") -> io.BytesIO:
        """テスト用の擬似音声ファイルを作成する"""
        return io.BytesIO(data)

    def test_returns_transcription_on_success(self) -> None:
        """Groq API が成功した場合、文字起こし結果を返すこと"""
        audio_file = self._make_audio_file()
        expected = "文字起こし結果のテキスト"

        with patch.object(app_module, "client") as mock_client:
            mock_client.audio.transcriptions.create.return_value = expected
            result = app_module.transcribe_audio(audio_file)

        assert result == expected

    def test_returns_none_on_exception(self) -> None:
        """Groq API が例外を送出した場合、None を返すこと"""
        audio_file = self._make_audio_file()

        with patch.object(app_module, "client") as mock_client:
            mock_client.audio.transcriptions.create.side_effect = Exception(
                "API エラー"
            )
            result = app_module.transcribe_audio(audio_file)

        assert result is None

    def test_calls_st_error_on_exception(self) -> None:
        """Groq API が例外を送出した場合、st.error が呼ばれること"""
        audio_file = self._make_audio_file()

        with patch.object(app_module, "client") as mock_client:
            mock_client.audio.transcriptions.create.side_effect = Exception(
                "接続エラー"
            )
            with patch.object(app_module, "st") as mock_st:
                app_module.transcribe_audio(audio_file)

        mock_st.error.assert_called_once()

    def test_api_called_with_correct_params(self) -> None:
        """Groq API が正しいパラメータで呼ばれること"""
        audio_file = self._make_audio_file()

        with patch.object(app_module, "client") as mock_client:
            mock_client.audio.transcriptions.create.return_value = "結果"
            app_module.transcribe_audio(audio_file)

        call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
        assert call_kwargs.get("model") == "whisper-large-v3"
        assert call_kwargs.get("language") == "ja"
        assert call_kwargs.get("response_format") == "text"
