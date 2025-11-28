from discord.ext import commands
from typing import Optional
import random

COIN = ["<:coin_heads:1443604984858939474>", "<:coin_tails:1443604986578600076>"]


class CoinFlip(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="coinflip", description="Flip a coin", aliases=["flip", "cf"]
    )
    async def coinflip(self, ctx: commands.Context, amount: Optional[int] = 1):
        if not 1 <= amount <= 10:
            return await ctx.reply(
                "Please enter a valid number of coins to flip (1-10)"
            )

        result = " ".join(random.choice(COIN) for _ in range(amount))
        await ctx.reply(result, mention_author=False)


async def setup(bot):
    await bot.add_cog(CoinFlip(bot))
