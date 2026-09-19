import sys
import discord
from discord.ext import commands

from config import (
    logger,
    DISCORD_BOT_TOKEN,
    ALLOWED_CHANNEL_IDS,
)
from cogs.chat import Chat
from cogs.admin import Admin
from cogs.owner import Owner

intents = discord.Intents.default()
intents.message_content = True


class SimbaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.allowed_channels = ALLOWED_CHANNEL_IDS
        self.chat_cog = None

    async def setup_hook(self):
        
        self.chat_cog = Chat(self)
        await self.add_cog(self.chat_cog)
        await self.add_cog(Admin(self, self.chat_cog))
        await self.add_cog(Owner(self,self.chat_cog))
        logger.info("✅ Cogs loaded successfully")

    async def on_ready(self):
        logger.info(f"✅ Logged in as {self.user} ({self.user.id})")


def main():
    if not DISCORD_BOT_TOKEN:
        logger.critical("❌ DISCORD_BOT_TOKEN missing")
        sys.exit(1)

    bot = SimbaBot()
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
