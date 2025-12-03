import discord
from discord.ext import commands
from typing import Optional
from googletrans import Translator, LANGUAGES


class Translate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="translate",
        description="Translate a message or some text to English",
        aliases=["tr"],
    )
    async def translate(self, ctx: commands.Context, *, text: Optional[str] = None):
        if not text and not ctx.message.reference:
            return await ctx.reply(
                "Please provide some text or a message", mention_author=False
            )

        async with Translator() as translator:
            src_text = (
                text
                if text
                else (
                    await ctx.channel.fetch_message(ctx.message.reference.message_id)
                ).content
            )
            src_lang = (await translator.detect(src_text)).lang
            translated = (await translator.translate(src_text, dest="en")).text

            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"Translated from {LANGUAGES.get(src_lang).capitalize()} -> English",
                description=f"**Translation:**\n```{translated.capitalize()}```",
            )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name} • Provided by CalcioBot"
            )

            await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(Translate(bot))
