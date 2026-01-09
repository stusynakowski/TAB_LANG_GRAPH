import os
import pytest
from tab_lang_graph.config import Settings

def test_default_settings():
    settings = Settings()
    assert settings.LG_HOST == "127.0.0.1"
    assert settings.LG_PORT == 8000

def test_env_override():
    os.environ["LG_PORT"] = "9090"
    # pydantic-settings reads os.environ
    settings = Settings()
    assert settings.LG_PORT == 9090
    del os.environ["LG_PORT"]
