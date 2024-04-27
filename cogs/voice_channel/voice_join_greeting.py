from gtts import gTTS

import discord
from discord.ext import commands
from cogs.voice_channel.base import BaseVoiceChannelCog


class VoiceJoinGreetingsCog(BaseVoiceChannelCog):

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            if after.channel:
                voice_client = discord.utils.get(self.bot.voice_clients, guild=member.guild)
                if not voice_client or not voice_client.is_connected():
                    voice_channel = after.channel
                    voice_client = await voice_channel.connect()
                    self.bot.logger.info(f"I have connected to {voice_channel.name}")
                    await self.say_hi(voice_client)
                personal_greeting = await self.create_greeting(member)
                await self.queue_audio(personal_greeting, voice_client)

    async def say_hi(self, voice_client):
        await self.queue_audio('/app/data/audio/hello.mp3', voice_client)

    async def create_greeting(self, member):
        self.bot.logger.info(f'Trying to create a custom greeting for {member.display_name}')
        tts = gTTS(f'Нова видрочка {member.display_name} приєдналась!', lang='uk')
        file_path = f'/app/data/audio/{member.display_name}-hello.mp3'
        tts.save(file_path)
        self.bot.logger.info(f'Greeting created {file_path}')
        return file_path


def setup(bot):
    bot.add_cog(VoiceJoinGreetingsCog(bot))
