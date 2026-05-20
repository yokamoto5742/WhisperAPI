import configparser
import os
import tempfile
from typing import Optional

from external_service.groq_api import setup_groq_client, transcribe_audio


def _load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), "..", "utils", "config.ini")
    config.read(config_path, encoding="utf-8")
    return config


def transcribe_uploaded_file(uploaded_file) -> Optional[str]:
    suffix = os.path.splitext(uploaded_file.name)[1] or ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        config = _load_config()
        client = setup_groq_client()
        return transcribe_audio(tmp_path, config, client)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
