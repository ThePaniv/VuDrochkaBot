"""The Discord bot subclass and cog wiring."""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

from vudrochka_bot.cogs.greetings import GreetingsCog
from vudrochka_bot.cogs.voice_status import VoiceStatusCog
from vudrochka_bot.config import Settings

log = logging.getLogger("vudrochka_bot")


def _build_intents() -> discord.Intents:
    """Minimal intents: we only need voice-state events.

    ``Intents.default()`` already includes ``voice_states`` and ``guilds`` and
    requires no privileged-intent toggles in the developer portal.
    """
    return discord.Intents.default()


class VuDrochkaBot(commands.Bot):
    """Loads the voice-status cog always, and greetings when enabled."""

    def __init__(self, settings: Settings) -> None:
        super().__init__(
            command_prefix=settings.command_prefix,
            intents=_build_intents(),
            help_command=None,
        )
        self.settings = settings

    async def setup_hook(self) -> None:
        await self.add_cog(VoiceStatusCog(self))
        if self.settings.enable_greetings:
            await self.add_cog(GreetingsCog(self))
            log.info("Greetings enabled (voice %s)", self.settings.tts_voice)
        else:
            log.info("Greetings disabled (set ENABLE_GREETINGS=true to turn on)")

    async def on_ready(self) -> None:
        if self.user is not None:
            log.info("Logged in as %s (ID: %s)", self.user, self.user.id)
