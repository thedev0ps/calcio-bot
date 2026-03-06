import discord
from discord.ext import commands
from typing import Optional
import aiohttp


class WouldYouRather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_wyr_messages = set()

    async def fetch_wyr(self, rating) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.truthordarebot.xyz/v1/wyr?rating={rating}"
            ) as response:
                data = await response.json()
                question = data["question"]

        return question

    def calculate_percentages(self, blue_votes: int, red_votes: int):
        total_votes = blue_votes + red_votes

        if total_votes == 0:
            return 50, 50

        blue_percent = round((blue_votes / total_votes) * 100)
        red_percent = 100 - blue_percent

        return blue_percent, red_percent

    def generate_bar(self, blue_votes: int, red_votes: int):
        total_votes = blue_votes + red_votes

        if total_votes == 0:
            blue_squares = 6
            red_squares = 6
        else:
            blue_squares = round((blue_votes / total_votes) * 12)
            red_squares = 12 - blue_squares

        return "🟦" * blue_squares + "🟥" * red_squares

    @commands.hybrid_command(
        name="wouldyourather",
        description="Get a random would you rather question",
        aliases=["wyr"],
    )
    async def wouldyourather(self, ctx: commands.Context, rating: Optional[str] = ""):
        if rating.lower() not in ["", "pg", "pg13", "r"]:
            return await ctx.reply(
                "The avaiable ratings are PG, PG13 and R (Leave empty for random rating)",
                mention_author=False,
            )

        question = await self.fetch_wyr(rating)

        if question.lower().startswith("would you rather"):
            option_1, option_2 = question[17:].lower().split(" or ")
        else:
            option_1, option_2 = question.lower().split(" or ")

        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Would you rather",
            description=f""":blue_circle: {option_1.capitalize()}?
OR
:red_circle: {option_2.capitalize()}

50%{' ' * 50}50%
🟦🟦🟦🟦🟦🟦🟥🟥🟥🟥🟥🟥""",
        )

        embed.set_footer(text="Vote by reacting to the message below")

        message = await ctx.reply(embed=embed, mention_author=False)

        self.active_wyr_messages.add(message.id)

        await message.add_reaction("🔵")
        await message.add_reaction("🔴")

    async def update_poll_embed(self, message: discord.Message):
        blue_votes = 0
        red_votes = 0

        for reaction in message.reactions:
            if str(reaction.emoji) == "🔵":
                blue_votes = reaction.count - 1
            elif str(reaction.emoji) == "🔴":
                red_votes = reaction.count - 1

        blue_percent, red_percent = self.calculate_percentages(blue_votes, red_votes)

        bar = self.generate_bar(blue_votes, red_votes)

        left_text = f"{blue_percent}%"
        right_text = f"{red_percent}%"

        total_width = 60
        spacing = total_width - len(left_text) - len(right_text)
        if spacing < 1:
            spacing = 1

        percent_line = f"{left_text}{' ' * spacing}{right_text}"

        embed = message.embeds[0]

        lines = embed.description.split("\n")
        question_part = "\n".join(lines[:3])

        embed.description = f"{question_part}\n\n" f"{percent_line}\n" f"{bar}"

        await message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in self.active_wyr_messages:
            return

        if str(payload.emoji) not in ["🔵", "🔴"]:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(payload.channel_id)

        message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            if str(reaction.emoji) != str(payload.emoji) and str(reaction.emoji) in [
                "🔵",
                "🔴",
            ]:
                member = payload.member
                if member:
                    await message.remove_reaction(reaction.emoji, member)

        await self.update_poll_embed(message)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id not in self.active_wyr_messages:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(payload.channel_id)

        message = await channel.fetch_message(payload.message_id)

        await self.update_poll_embed(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        self.active_wyr_messages.discard(payload.message_id)


async def setup(bot):
    await bot.add_cog(WouldYouRather(bot))
