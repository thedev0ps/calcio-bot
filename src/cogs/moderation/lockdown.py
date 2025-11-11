import discord
from discord.ext import commands
from typing import Optional


class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="lock", description="Lockdown a specified channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(
        self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None
    ):
        channel = channel or ctx.channel
        overwrites = channel.overwrites_for(ctx.guild.default_role)

        if overwrites.send_messages:
            overwrites.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            await ctx.send(f":lock: {channel.mention} has been locked")

        else:
            await ctx.send(f"{channel.mention} is already locked")

    @commands.hybrid_command(name="unlock", description="unlock a specified channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(
        self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None
    ):
        channel = channel or ctx.channel
        overwrites = channel.overwrites_for(ctx.guild.default_role)

        if not overwrites.send_messages:
            overwrites.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            await ctx.send(f":unlock: {channel.mention} has been unlocked")

        else:
            await ctx.send(f"{channel.mention} is already unlocked")


async def setup(bot):
    await bot.add_cog(Lockdown(bot))
