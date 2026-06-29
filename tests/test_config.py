"""Tests for environment-driven configuration."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from vudrochka_bot.config import Settings


def test_missing_token_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)  # type: ignore[call-arg]


def test_loads_and_coerces(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "super-secret")
    monkeypatch.setenv("ENABLE_GREETINGS", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.bot_token.get_secret_value() == "super-secret"
    assert settings.enable_greetings is True
    assert settings.log_level == "DEBUG"
    assert "{name}" in settings.tts_greeting_template


def test_token_not_leaked_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "super-secret")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert "super-secret" not in repr(settings)
