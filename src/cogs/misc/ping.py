import discord
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Displays the bots latency")
    async def ping(self, ctx):
        await ctx.send(
            f":ping_pong: **Pong!** {int(self.bot.latency * 1000)} ms",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Ping(bot))
