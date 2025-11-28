import discord
from discord.ext import commands
import aiohttp


class EightBall(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def shake_ball(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://eightballapi.com/api?locale=en"
            ) as response:
                data = await response.json()
                answer = data["reading"]

        return answer

    @commands.hybrid_command(
        name="eightball",
        description="Ask the magic 8 ball for its wisdom",
        aliases=["8ball"],
    )
    async def eightball(self, ctx: commands.Context, *, question: str = None):
        if not question or not question.strip():
            return await ctx.reply("Please provide a question", mention_author=False)

        answer = await self.shake_ball()
        await ctx.reply(answer, mention_author=False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user in message.mentions and "?" in message.content:
            answer = await self.shake_ball()
            await message.reply(answer, mention_author=False)


async def setup(bot):
    await bot.add_cog(EightBall(bot))
