import aiohttp
from discord.ext import commands

from utils.json_utils import load_json
from configs import VuDrochkaBotConfigs
from cogs.voice_channel import VoiceChannelConfigs


class VoiceStateUpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ending_mapping = load_json(VoiceChannelConfigs.VUDROCHKA_ENDINGS_JSON_FILE_PATH)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None or after.channel is not None:
            channel = after.channel or before.channel
            amount_of_members = len(channel.members)
            new_name = amount_of_members * ":otter:" + self.ending_mapping[str(amount_of_members)]
            successful = await self.edit_channel_status(str(channel.id), new_name)
            if successful:
                self.bot.logger.info(f'Changed voice channel name to "{new_name}"')
            else:
                self.bot.logger.info(f'Can`t change voice channel name to "{new_name}"')

    async def edit_channel_status(self, channel_id, new_name):
        url = f"{VuDrochkaBotConfigs.DISCORD_API_URL}/channels/{channel_id}/voice-status"
        body = {"status": new_name}
        headers = {"authorization": VuDrochkaBotConfigs.DISCORD_WEB_USER_TOKEN}
        async with aiohttp.ClientSession() as session:
            async with session.put(url=url, json=body, headers=headers) as res:
                if res.status != 204:
                    self.bot.logger.error('Can`t edit. Status code:', res.status)
                    response_text = await res.json()
                    self.bot.logger.error('Body:', response_text)
                    return False
        return True


def setup(bot):
    bot.add_cog(VoiceStateUpdateCog(bot))
