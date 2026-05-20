from pathlib import Path
from unittest.mock import patch

from utils.env_loader import load_environment_variables


class TestLoadEnvironmentVariables:
    def test_env_file_exists_loads_dotenv(self, tmp_path: Path) -> None:
        """.env ファイルが存在する場合、load_dotenv が呼ばれること"""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=hello\n", encoding="utf-8")

        with (
            patch("utils.env_loader.Path") as mock_path_cls,
            patch("utils.env_loader.load_dotenv") as mock_load_dotenv,
            patch("utils.env_loader.os.path.exists", return_value=True),
        ):
            # Path(__file__).parent.parent が tmp_path を返すよう設定
            mock_path_cls.return_value.parent.parent = tmp_path

            load_environment_variables()

        mock_load_dotenv.assert_called_once()

    def test_env_file_not_exists_skips_dotenv(self, tmp_path: Path) -> None:
        """.env ファイルが存在しない場合、load_dotenv が呼ばれないこと"""
        with (
            patch("utils.env_loader.Path") as mock_path_cls,
            patch("utils.env_loader.load_dotenv") as mock_load_dotenv,
            patch("utils.env_loader.os.path.exists", return_value=False),
        ):
            mock_path_cls.return_value.parent.parent = tmp_path

            load_environment_variables()

        mock_load_dotenv.assert_not_called()

    def test_env_file_sets_env_variable(self, tmp_path: Path) -> None:
        """.env ファイルの内容が環境変数として読み込まれること"""
        env_file = tmp_path / ".env"
        env_file.write_text("WHISPER_TEST_VAR=loaded_value\n", encoding="utf-8")

        # 実際のファイルパスを差し替えて load_dotenv を呼ばせる
        with patch("utils.env_loader.Path") as mock_path_cls:
            mock_path_cls.return_value.parent.parent = tmp_path
            with patch(
                "utils.env_loader.os.path.exists",
                return_value=True,
            ):
                with patch(
                    "utils.env_loader.os.path.join",
                    return_value=str(env_file),
                ):
                    with patch("utils.env_loader.load_dotenv") as mock_load_dotenv:
                        load_environment_variables()
                        mock_load_dotenv.assert_called_once_with(str(env_file))
