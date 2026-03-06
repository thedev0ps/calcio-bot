import discord
from discord.ext import commands
from typing import Optional
import aiohttp


class TruthOrDare(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def fetch_truth(self, rating) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.truthordarebot.xyz/v1/truth?rating={rating}"
            ) as response:
                data = await response.json()
                question = data["question"]

        return question

    async def fetch_dare(self, rating) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.truthordarebot.xyz/v1/dare?rating={rating}"
            ) as response:
                data = await response.json()
                question = data["question"]

        return question

    @commands.hybrid_command(
        name="truth", description="Get a random truth question (Truth or Dare)"
    )
    async def truth(self, ctx: commands.Context, rating: Optional[str] = ""):
        if rating.lower() not in ["", "pg", "pg13", "r"]:
            return await ctx.reply(
                "The avaiable ratings are PG, PG13 and R (Leave empty for random rating)",
                mention_author=False,
            )

        truth = await self.fetch_truth(rating)
        await ctx.reply(truth, mention_author=False)

    @commands.hybrid_command(
        name="dare", description="Get a random dare question (Truth or Dare)"
    )
    async def dare(self, ctx: commands.Context, rating: Optional[str] = ""):
        if rating.lower() not in ["", "pg", "pg13", "r"]:
            return await ctx.reply(
                "The avaiable ratings are PG, PG13 and R (Leave empty for random rating)",
                mention_author=False,
            )

        dare = await self.fetch_dare(rating)
        await ctx.reply(dare, mention_author=False)


async def setup(bot):
    await bot.add_cog(TruthOrDare(bot))
