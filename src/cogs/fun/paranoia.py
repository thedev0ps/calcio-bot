import discord
from discord.ext import commands
from typing import Optional
import aiohttp


class Paranoia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_wyr(self, rating) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.truthordarebot.xyz/v1/paranoia?rating={rating}"
            ) as response:
                data = await response.json()
                question = data["question"]

        return question

    @commands.hybrid_command(
        name="paranoia",
        description="Get a random paranoia question",
    )
    async def paranoia(self, ctx: commands.Context, rating: Optional[str] = ""):
        if rating.lower() not in ["", "pg", "pg13", "r"]:
            return await ctx.reply(
                "The avaiable ratings are PG, PG13 and R (Leave empty for random rating)",
                mention_author=False,
            )

        question = await self.fetch_wyr(rating)

        await ctx.reply(question, mention_author=False)


async def setup(bot):
    await bot.add_cog(Paranoia(bot))
