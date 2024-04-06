import os
from dotenv import load_dotenv

load_dotenv()


class VoiceChannelConfigs:
    VUDROCHKA_ENDINGS_JSON_FILE_PATH = os.environ.get('VUDROCHKA_ENDINGS_JSON_FILE_PATH')


class VuDrochkaBotConfigs:
    DISCORD_API_URL = os.environ.get("DISCORD_API_URL", "https://discord.com/api/v9")
    DISCORD_WEB_USER_TOKEN = os.environ.get("DISCORD_WEB_USER_TOKEN")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
