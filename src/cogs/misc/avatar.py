import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="avatar",
        description="Displays the user's profile picture",
        aliases=["av", "pfp"],
    )
    @app_commands.describe(user="The member/user whose avatar you want to view")
    async def avatar(self, ctx: commands.Context, user: Optional[discord.User] = None):
        user = user or ctx.author
        embed = discord.Embed(
            color=discord.Color.blue(), title=f"{user.display_name}'s avatar:"
        )
        embed.set_image(url=user.display_avatar.replace(size=256))
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name} • Provided by CalcioBot",
        )
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(Avatar(bot))
