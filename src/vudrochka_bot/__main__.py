"""Entry point: ``python -m vudrochka_bot`` (or the ``vudrochka-bot`` script)."""

from __future__ import annotations

import logging

from vudrochka_bot.bot import VuDrochkaBot
from vudrochka_bot.config import get_settings
from vudrochka_bot.logging_config import setup_logging

log = logging.getLogger("vudrochka_bot")


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    bot = VuDrochkaBot(settings)
    # We configured logging ourselves, so tell discord.py not to add its own.
    bot.run(settings.bot_token.get_secret_value(), log_handler=None)


if __name__ == "__main__":
    main()
