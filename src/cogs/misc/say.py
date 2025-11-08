import discord
from discord.ext import commands
from typing import Optional


class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="say", description="Send a message through the bot")
    @commands.has_permissions(manage_messages=True)
    async def say(
        self,
        ctx: commands.Context,
        message: str,
        channel: Optional[discord.TextChannel] = None,
    ):
        if channel is None:
            await ctx.send(message)
        else:
            await self.bot.get_channel(channel.id).send(message)


async def setup(bot):
    await bot.add_cog(Say(bot))
