"""Join a voice channel and greet each member with a neural-TTS message."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from importlib.resources import as_file, files
from pathlib import Path

import discord
from discord.ext import commands

from vudrochka_bot.services.audio import AudioJob, AudioPlayer
from vudrochka_bot.services.tts import TTSService

log = logging.getLogger("vudrochka_bot.greetings")


def _hello_chime() -> Path | None:
    """Path to the bundled hello chime, or ``None`` if it isn't packaged."""
    try:
        resource = files("vudrochka_bot.assets") / "hello.mp3"
        with as_file(resource) as path:
            if path.is_file():
                return path
    except (FileNotFoundError, ModuleNotFoundError):
        pass
    return None


class GreetingsCog(commands.Cog):
    """Connects to a joiner's channel and plays a personalized TTS greeting.

    Fixes from the original implementation:

    * only reacts to genuine joins/moves (not mute/deafen/stream toggles);
    * an ``asyncio.Lock`` per guild prevents the "already connected" race when
      several members join at once;
    * greeting audio is written to a temp file and deleted after playback
      (member id is never used as a path), so there's no path-traversal or
      disk-fill vector;
    * leaves the channel automatically once no humans remain.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.tts = TTSService(bot.settings.tts_voice)  # type: ignore[attr-defined]
        self._players: dict[int, AudioPlayer] = {}
        self._locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if member.bot or before.channel == after.channel:
            return

        # Someone left/moved out: drop the connection if the bot is now alone.
        if before.channel is not None:
            await self._leave_if_alone(member.guild)

        # Someone joined/moved in: greet them.
        if isinstance(after.channel, discord.VoiceChannel):
            await self._greet(member, after.channel)

    async def _greet(self, member: discord.Member, channel: discord.VoiceChannel) -> None:
        player = await self._ensure_connected(member.guild, channel)
        if player is None:
            return

        template: str = self.bot.settings.tts_greeting_template  # type: ignore[attr-defined]
        text = template.format(name=member.display_name)
        try:
            audio_path = await self.tts.synthesize(text)
        except Exception:
            log.exception("TTS synthesis failed for %s", member.display_name)
            return

        player.submit(AudioJob(path=audio_path, cleanup=True))
        log.info("Queued greeting for %s in #%s", member.display_name, channel.name)

    async def _ensure_connected(
        self, guild: discord.Guild, channel: discord.VoiceChannel
    ) -> AudioPlayer | None:
        async with self._locks[guild.id]:
            voice_client = guild.voice_client
            is_live = isinstance(voice_client, discord.VoiceClient) and voice_client.is_connected()

            if not is_live:
                try:
                    voice_client = await channel.connect()
                except discord.ClientException:
                    voice_client = guild.voice_client  # lost a race; reuse the winner
                if not isinstance(voice_client, discord.VoiceClient):
                    return None
                log.info("Connected to #%s", channel.name)
                player = AudioPlayer(voice_client)
                self._players[guild.id] = player
                chime = _hello_chime()
                if self.bot.settings.join_chime and chime is not None:  # type: ignore[attr-defined]
                    player.submit(AudioJob(path=chime, cleanup=False))
                return player

            # Already connected — reuse the player, recreating it if the voice
            # client object changed (e.g. after a reconnect).
            player = self._players.get(guild.id)
            if player is None or player.voice_client is not voice_client:
                player = AudioPlayer(voice_client)  # type: ignore[arg-type]
                self._players[guild.id] = player
            return player

    async def _leave_if_alone(self, guild: discord.Guild) -> None:
        voice_client = guild.voice_client
        if not isinstance(voice_client, discord.VoiceClient) or voice_client.channel is None:
            return
        if any(not m.bot for m in voice_client.channel.members):
            return

        async with self._locks[guild.id]:
            player = self._players.pop(guild.id, None)
            if player is not None:
                await player.aclose()
            await voice_client.disconnect(force=True)
            log.info("Left voice in guild %s (no members remaining)", guild.id)
