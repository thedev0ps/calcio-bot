import discord
from discord.ext import commands
import aiohttp


class DadJoke(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def fetch_joke(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://icanhazdadjoke.com/", headers={"Accept": "application/json"}
            ) as response:
                data = await response.json()
                joke = data["joke"]

        return joke

    @commands.hybrid_command(name="dadjoke", description="Get a random dad joke")
    async def dadjoke(self, ctx: commands.Context):
        joke = await self.fetch_joke()
        await ctx.reply(joke, mention_author=False)


async def setup(bot):
    await bot.add_cog(DadJoke(bot))
