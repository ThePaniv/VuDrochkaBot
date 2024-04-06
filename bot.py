import logging
import discord
from discord.ext import commands
from configs import VuDrochkaBotConfigs
from cogs.voice_channel.voice_state_update_cog import VoiceStateUpdateCog


class VuDrochkaBot(commands.Bot):

    def __init__(self, command_prefix, intents=discord.Intents.default()):
        super().__init__(command_prefix, intents=intents)
        self.logger = logging.getLogger('discord')

    async def setup_hook(self):
        await self.add_cog(VoiceStateUpdateCog(self))
        self.logger.info("Setup tasks complete.")

    async def on_ready(self):
        self.logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        self.logger.info('------')


if __name__ == '__main__':
    bot = VuDrochkaBot(command_prefix='!')
    bot.run(VuDrochkaBotConfigs.BOT_TOKEN)
