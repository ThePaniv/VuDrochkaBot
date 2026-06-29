"""Rename a voice channel's status to an otter-count whenever it changes."""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

from vudrochka_bot.pluralization import format_status

log = logging.getLogger("vudrochka_bot.voice_status")


class VoiceStatusCog(commands.Cog):
    """Keeps each voice channel's status in sync with its member count.

    Uses the official ``VoiceChannel.edit(status=...)`` API (discord.py >= 2.4)
    with the *bot* token — no user/self-bot token, no hand-rolled HTTP. Requires
    the bot to hold the "Set Voice Channel Status" permission in the guild.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        # Only the channel membership matters. Mute/deafen/stream toggles leave
        # the channel unchanged, so skip them to avoid hammering the API.
        if before.channel == after.channel:
            return

        # A move touches two channels; a join/leave touches one. ``dict.fromkeys``
        # de-duplicates while preserving order and dropping ``None``.
        for channel in dict.fromkeys((before.channel, after.channel)):
            if isinstance(channel, discord.VoiceChannel):
                await self._update_status(channel)

    async def _update_status(self, channel: discord.VoiceChannel) -> None:
        status = format_status(len(channel.members))
        try:
            await channel.edit(status=status, reason="member count changed")
        except discord.Forbidden:
            log.warning(
                "Missing 'Set Voice Channel Status' permission in #%s (%s)",
                channel.name,
                channel.id,
            )
        except discord.HTTPException:
            log.exception("Failed to set status for #%s", channel.name)
        else:
            log.info('Set status of #%s to "%s"', channel.name, status)
