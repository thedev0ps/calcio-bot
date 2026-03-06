import discord
from discord.ext import commands
from typing import Optional
import aiohttp


class NeverHaveIEver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_nhie_messages = set()

    async def fetch_wyr(self, rating) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.truthordarebot.xyz/v1/nhie?rating={rating}"
            ) as response:
                data = await response.json()
                question = data["question"]

        return question

    def calculate_percentages(self, i_have_votes: int, i_havent_votes: int):
        total_votes = i_have_votes + i_havent_votes

        if total_votes == 0:
            return 50, 50

        i_have_percent = round((i_have_votes / total_votes) * 100)
        i_havent_percent = 100 - i_have_percent

        return i_have_percent, i_havent_percent

    def generate_bar(self, i_have_votes: int, i_havent_votes: int):
        total_votes = i_have_votes + i_havent_votes

        if total_votes == 0:
            yellow_squares = 6
            white_squares = 6
        else:
            yellow_squares = round((i_have_votes / total_votes) * 12)
            white_squares = 12 - yellow_squares

        return "🟨" * yellow_squares + "⬜️" * white_squares

    @commands.hybrid_command(
        name="neverhaveiever",
        description="Get a random would you rather question",
        aliases=["nhie"],
    )
    async def NeverHaveIEver(self, ctx: commands.Context, option: Optional[str] = ""):
        option = option.strip()

        if option.lower() in ["", "pg", "pg13", "r"]:
            question = await self.fetch_wyr(option)
        else:
            question = option.capitalize()

        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Never Have I Ever",
            description=f"""{question}

50%{' ' * 50}50%
🟨🟨🟨🟨🟨🟨⬜️⬜️⬜️⬜️⬜️⬜️""",
        )

        embed.set_footer(text="Vote by reacting to the message below")

        message = await ctx.reply(embed=embed, mention_author=False)

        self.active_nhie_messages.add(message.id)

        await message.add_reaction("✋")
        await message.add_reaction("✊")

    async def update_poll_embed(self, message: discord.Message):
        i_have_votes = 0
        i_havent_votes = 0

        for reaction in message.reactions:
            if str(reaction.emoji) == "✋":
                i_have_votes = reaction.count - 1
            elif str(reaction.emoji) == "✊":
                i_havent_votes = reaction.count - 1

        i_have_percent, i_havent_percent = self.calculate_percentages(
            i_have_votes, i_havent_votes
        )

        bar = self.generate_bar(i_have_votes, i_havent_votes)

        left_text = f"{i_have_percent}%"
        right_text = f"{i_havent_percent}%"
        total_width = 50
        spacing = total_width - len(left_text) - len(right_text)
        if spacing < 1:
            spacing = 1

        percent_line = f"{left_text}{' ' * spacing}{right_text}"

        embed = message.embeds[0]

        question_part = embed.description.split("\n\n")[0]

        embed.description = f"{question_part}\n\n{percent_line}\n{bar}"

        await message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in self.active_nhie_messages:
            return

        if str(payload.emoji) not in ["✋", "✊"]:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(payload.channel_id)

        message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            if str(reaction.emoji) != str(payload.emoji) and str(reaction.emoji) in [
                "✋",
                "✊",
            ]:
                member = payload.member
                if member:
                    await message.remove_reaction(reaction.emoji, member)

        await self.update_poll_embed(message)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id not in self.active_nhie_messages:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            channel = await self.bot.fetch_channel(payload.channel_id)

        message = await channel.fetch_message(payload.message_id)

        await self.update_poll_embed(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        self.active_nhie_messages.discard(payload.message_id)


async def setup(bot):
    await bot.add_cog(NeverHaveIEver(bot))
