import time
import asyncio
from discord.ext import commands
from discord import FFmpegPCMAudio


class BaseVoiceChannelCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.audio_queue = asyncio.Queue()
        self.is_playing = False

    async def play_audio(self, voice_client):
        while True:
            audio_path = await self.audio_queue.get()
            if voice_client.is_connected():
                audio_source = FFmpegPCMAudio(audio_path)
                voice_client.play(audio_source,
                                  after=lambda e: self.bot.loop.call_soon_threadsafe(self.audio_queue.task_done))
                while voice_client.is_playing():
                    await asyncio.sleep(1)
            else:
                break

    async def queue_audio(self, audio_path, voice_client):
        await self.audio_queue.put(audio_path)
        if not self.is_playing:
            self.is_playing = True
            self.bot.loop.create_task(self.play_audio(voice_client))
