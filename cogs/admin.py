from discord.ext import commands
from utils.helpers import is_admin


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot, chat_cog):
        self.bot = bot
        self.chat = chat_cog

    async def admin_check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        if not is_admin(ctx.author):
            await ctx.send("❌ Only Moderators are allowed to run commands!")
            return False
        return True
    

    @commands.command()
    async def clearcontext(self, ctx):
        if not await self.admin_check(ctx):
            return
        self.chat.contexts.clear()
        await ctx.send("🧠 Context cleared.")

    
    @commands.command()
    async def activate(self, ctx):
        if not await self.admin_check(ctx):
            return

        gid = ctx.guild.id
        self.chat.guild_active[gid] = True
        await ctx.send("Chat activated!")

    
    @commands.command()
    async def deactivate(self, ctx):
        if not await self.admin_check(ctx):
            return

        gid = ctx.guild.id
        self.chat.guild_active[gid] = False
        await ctx.send("Chat deactivated...")
        
    


