"""Smoke test: every module imports cleanly (catches syntax/import errors)."""

from __future__ import annotations


def test_package_imports() -> None:
    import vudrochka_bot
    from vudrochka_bot import bot, config, logging_config, pluralization  # noqa: F401
    from vudrochka_bot.cogs import greetings, voice_status  # noqa: F401
    from vudrochka_bot.services import audio, tts  # noqa: F401

    assert vudrochka_bot.__version__
