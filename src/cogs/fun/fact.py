from discord.ext import commands
import aiohttp


class Fact(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_fact(self) -> str:
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                "https://uselessfacts.jsph.pl/api/v2/facts/random"
            )
            response = await response.json()
            fact = response["text"]

        return fact

    @commands.hybrid_command(
        name="fact", description="Get a random useless fact", aliases=["funfact"]
    )
    async def fact(self, ctx: commands.Context):
        fact = await self.get_fact()
        await ctx.reply(fact, mention_author=False)


async def setup(bot):
    await bot.add_cog(Fact(bot))
