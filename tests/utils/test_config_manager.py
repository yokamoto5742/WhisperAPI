import configparser
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from utils.config_manager import ConfigManager, get_config_path, get_config_value


def _write_ini(path: Path, content: str, encoding: str = "utf-8") -> None:
    path.write_text(content, encoding=encoding)


class TestGetConfigPath:
    def test_normal_returns_config_ini_path(self) -> None:
        """通常実行時、utils/ 直下の config.ini パスを返すこと"""
        result = get_config_path()
        assert result.name == "config.ini"
        assert result.parent.name == "utils"

    def test_frozen_returns_meipass_config_ini(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """frozen 実行時、sys._MEIPASS 配下の config.ini パスを返すこと"""
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

        result = get_config_path()

        assert result == tmp_path / "config.ini"


class TestConfigManagerInit:
    def test_init_loads_config(self, tmp_path: Path) -> None:
        """__init__ でファイルが正常に読み込まれること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\nsome_key = some_value\n")

        manager = ConfigManager(config_file)

        assert manager.config.get("Paths", "some_key") == "some_value"

    def test_init_raises_when_file_not_found(self, tmp_path: Path) -> None:
        """存在しないファイルを指定した場合 FileNotFoundError が送出されること"""
        with pytest.raises(FileNotFoundError):
            ConfigManager(tmp_path / "nonexistent.ini")


class TestLoadConfig:
    def test_utf8_file_is_read(self, tmp_path: Path) -> None:
        """UTF-8 エンコードの config.ini が正常に読み込まれること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Section]\nkey = 値\n", encoding="utf-8")

        manager = ConfigManager(config_file)

        assert manager.config.get("Section", "key") == "値"

    def test_cp932_fallback(self, tmp_path: Path) -> None:
        """UTF-8 で読めないバイト列の場合、CP932 フォールバックで読み込まれること"""
        config_file = tmp_path / "config.ini"
        # CP932 でエンコードした日本語テキスト（UTF-8 では不正バイト列）
        content_bytes = "[Paths]\npath = あ\n".encode("cp932")
        config_file.write_bytes(content_bytes)

        manager = ConfigManager(config_file)

        assert manager.config.get("Paths", "path") == "あ"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        """ファイルが存在しない場合 FileNotFoundError が送出されること"""
        manager = ConfigManager.__new__(ConfigManager)
        manager.config_file = tmp_path / "missing.ini"
        manager.config = configparser.ConfigParser()

        with pytest.raises(FileNotFoundError):
            manager.load_config()


class TestSaveConfig:
    def test_save_writes_utf8(self, tmp_path: Path) -> None:
        """save_config が UTF-8 でファイルを書き込むこと"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\nkey = 初期値\n")

        manager = ConfigManager(config_file)
        manager.config.set("Paths", "key", "更新値")
        manager.save_config()

        saved = config_file.read_text(encoding="utf-8")
        assert "更新値" in saved

    def test_save_raises_on_permission_error(self, tmp_path: Path) -> None:
        """書き込み失敗時に OSError が送出されること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\nkey = value\n")

        manager = ConfigManager(config_file)

        with patch("builtins.open", side_effect=IOError("permission denied")):
            with pytest.raises(OSError):
                manager.save_config()


class TestGetPath:
    def test_returns_path_from_paths_section(self, tmp_path: Path) -> None:
        """[Paths] セクションから Path オブジェクトが返されること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\noutput_dir = /tmp/output\n")

        manager = ConfigManager(config_file)
        result = manager.get_path("output_dir")

        assert result == Path("/tmp/output")

    def test_raises_when_key_not_found(self, tmp_path: Path) -> None:
        """存在しないキーを指定した場合 configparser.NoOptionError が送出されること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\n")

        manager = ConfigManager(config_file)

        with pytest.raises(configparser.NoOptionError):
            manager.get_path("nonexistent_key")


class TestGetTesseractPath:
    def test_returns_value_from_config(self, tmp_path: Path) -> None:
        """config.ini に値がある場合、その値が返されること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\ntesseract_path = /usr/bin/tesseract\n")

        manager = ConfigManager(config_file)

        assert manager.get_tesseract_path() == "/usr/bin/tesseract"

    def test_returns_fallback_when_key_missing(self, tmp_path: Path) -> None:
        """tesseract_path が未設定の場合、デフォルトパスが返されること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\n")

        manager = ConfigManager(config_file)

        assert "tesseract.exe" in manager.get_tesseract_path()


class TestSetTesseractPath:
    def test_sets_path_when_file_exists(self, tmp_path: Path) -> None:
        """実在するパスを指定した場合、config に保存されること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\n")

        fake_tesseract = tmp_path / "tesseract.exe"
        fake_tesseract.touch()

        manager = ConfigManager(config_file)
        manager.set_tesseract_path(fake_tesseract)

        assert manager.config.get("Paths", "tesseract_path") == str(fake_tesseract)

    def test_raises_when_file_not_exists(self, tmp_path: Path) -> None:
        """存在しないパスを指定した場合 FileNotFoundError が送出されること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\n")

        manager = ConfigManager(config_file)

        with pytest.raises(FileNotFoundError):
            manager.set_tesseract_path(tmp_path / "nonexistent_tesseract.exe")


class TestEnsureSection:
    def test_creates_section_if_absent(self, tmp_path: Path) -> None:
        """セクションが存在しない場合、作成されること"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[ExistingSection]\n")

        manager = ConfigManager(config_file)
        manager._ensure_section("NewSection")

        assert "NewSection" in manager.config

    def test_does_not_overwrite_existing_section(self, tmp_path: Path) -> None:
        """既存セクションが上書きされないこと"""
        config_file = tmp_path / "config.ini"
        _write_ini(config_file, "[Paths]\nkey = value\n")

        manager = ConfigManager(config_file)
        manager._ensure_section("Paths")

        assert manager.config.get("Paths", "key") == "value"


class TestGetConfigValue:
    def setup_method(self) -> None:
        self.config = configparser.ConfigParser()
        self.config["Section"] = {
            "bool_key": "true",
            "int_key": "42",
            "str_key": "hello",
        }

    def test_returns_bool_true_for_true_string(self) -> None:
        result = get_config_value(self.config, "Section", "bool_key", fallback=False)
        assert result is True

    def test_returns_bool_false_for_false_string(self) -> None:
        self.config["Section"]["bool_key"] = "false"
        result = get_config_value(self.config, "Section", "bool_key", fallback=True)
        assert result is False

    def test_returns_bool_true_for_1_string(self) -> None:
        self.config["Section"]["bool_key"] = "1"
        result = get_config_value(self.config, "Section", "bool_key", fallback=False)
        assert result is True

    def test_returns_int_value(self) -> None:
        result = get_config_value(self.config, "Section", "int_key", fallback=0)
        assert result == 42

    def test_returns_str_value(self) -> None:
        result = get_config_value(self.config, "Section", "str_key", fallback="")
        assert result == "hello"

    def test_returns_fallback_when_key_missing(self) -> None:
        result = get_config_value(
            self.config, "Section", "missing_key", fallback="default"
        )
        assert result == "default"

    def test_returns_fallback_when_section_missing(self) -> None:
        result = get_config_value(self.config, "NoSection", "any_key", fallback=99)
        assert result == 99

    def test_bool_fallback_takes_priority_over_int(self) -> None:
        """bool は int のサブクラスなので、fallback=True の場合は bool 判定になること"""
        self.config["Section"]["bool_key"] = "yes"
        result = get_config_value(self.config, "Section", "bool_key", fallback=True)
        assert result is True
