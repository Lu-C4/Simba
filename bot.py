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
        self.add_check(self._allowed_channel_check)
        self.chat_cog = None

    async def _allowed_channel_check(self, ctx: commands.Context) -> bool:
        if ctx.command and ctx.command.qualified_name in {"simba", "clearcontext"}:
            if (
                ctx.command.qualified_name == "clearcontext"
                and ctx.channel.id not in self.allowed_channels
            ):
                return await self.is_owner(ctx.author)
            return True
        return ctx.channel.id in self.allowed_channels

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
