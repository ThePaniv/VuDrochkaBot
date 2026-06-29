"""Typed application configuration, loaded from the environment / ``.env``."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """All runtime configuration.

    Values come from real environment variables first, then a local ``.env``
    file (handy for development). Missing required values raise a
    ``ValidationError`` at startup, so the bot fails fast instead of crashing
    later with an opaque error.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- required ---
    bot_token: SecretStr = Field(
        ...,
        description="Discord *bot* token (not a user token).",
    )

    # --- behaviour toggles ---
    enable_greetings: bool = Field(
        default=False,
        description="Join voice channels and play a TTS greeting for each joiner.",
    )
    join_chime: bool = Field(
        default=True,
        description="Play the bundled hello chime when the bot first connects.",
    )

    # --- text-to-speech ---
    tts_voice: str = Field(
        default="uk-UA-PolinaNeural",
        description="edge-tts voice (e.g. uk-UA-PolinaNeural or uk-UA-OstapNeural).",
    )
    tts_greeting_template: str = Field(
        default="Нова видрочка {name} приєдналась!",
        description="Greeting text; '{name}' is replaced with the member display name.",
    )

    # --- misc ---
    command_prefix: str = Field(default="!", description="Legacy text-command prefix.")
    log_level: LogLevel = Field(default="INFO", description="Root log level.")


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton (validated once)."""
    return Settings()  # type: ignore[call-arg]  # values are populated from the environment
