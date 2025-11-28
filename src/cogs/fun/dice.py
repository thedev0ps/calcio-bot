from discord.ext import commands
import random
from typing import Optional

DICE = [
    "<:dice_1:1443893529955926027>",
    "<:dice_2:1443893527548268747>",
    "<:dice_3:1443893526273196083>",
    "<:dice_4:1443893524457324619>",
    "<:dice_5:1443893523362353173>",
    "<:dice_6:1443893521735090207>",
]


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="dice", description="Roll a dice", aliases=["d"])
    async def dice(self, ctx: commands.Context, amount: Optional[int] = 1):
        if not 1 <= amount <= 10:
            return await ctx.reply(
                "Please enter a valid number of die to roll (1-10)",
                mention_author=False,
            )

        result = " ".join(random.choice(DICE) for _ in range(amount))
        await ctx.reply(result, mention_author=False)


async def setup(bot):
    await bot.add_cog(Dice(bot))
