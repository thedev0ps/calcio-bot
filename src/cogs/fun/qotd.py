import discord
from discord.ext import commands


class QOTD(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 1180934191081340978
        self.role_id = 1188393849786220604

    @commands.hybrid_command(
        name="qotd",
        description="Send the 'Question of the Day' queston",
        aliases=["questionoftheday"],
    )
    @commands.has_role(1183230742503899147)
    async def qotd(self, ctx: commands.Context, *, question: str):
        if not question.strip():
            return ctx.reply("Please provide a question to send.")

        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Question of the Day",
            description=question,
        )

        message = await self.bot.get_channel(self.channel_id).send(
            f"<@&{self.role_id}>", embed=embed
        )

        thread = await message.create_thread(name="Question of the Day")

        await thread.send("Answer today's Question of the Day here!")


async def setup(bot):
    await bot.add_cog(QOTD(bot))
