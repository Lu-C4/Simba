from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot, chat_cog):
        self.bot = bot
        self.chat = chat_cog
        
    @commands.command()
    @commands.is_owner()
    async def gdeactivate(self, ctx):
        
        self.chat.global_active = False
        await ctx.send("Chat globally deactivated.")
        
    @commands.command()
    @commands.is_owner()
    async def gactivate(self, ctx):
        
        self.chat.global_active = True
        await ctx.send("Chat globally activated.")