from discord.ext import commands
import aiohttp


class Yo_mama(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def fetch_joke(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.yomama-jokes.com/api/random"
            ) as response:
                data = await response.json()
                joke = data["joke"]

        return joke

    @commands.hybrid_command(
        name="yomama", description="Get a random Yo Mama joke", aliases=["joemama"]
    )
    async def yomama(self, ctx: commands.Context):
        joke = await self.fetch_joke()
        await ctx.reply(joke, mention_author=False)


async def setup(bot):
    await bot.add_cog(Yo_mama(bot))
