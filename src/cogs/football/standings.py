import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()


class Standings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_standings(self):
        teams = []
        url = "https://api.football-data.org/v4/competitions/SA/standings"
        headers = {"X-Auth-Token": os.getenv("FOOTBALL_DATA_API_KEY")}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response_json = await response.json()
                data = response_json["standings"][0]["table"]

        for team in data:
            teams.append(
                {
                    "position": team["position"],
                    "name": team["team"]["shortName"],
                    "played": team["playedGames"],
                    "won": team["won"],
                    "draw": team["draw"],
                    "lost": team["lost"],
                    "goals_for": team["goalsFor"],
                    "goals_against": team["goalsAgainst"],
                    "goal_diff": team["goalDifference"],
                    "points": team["points"],
                }
            )

        standings = ""
        for team in teams:
            standings += (
                f"\n{f"{team["position"]}.":<4}"
                f"{team["name"]:<12}"
                f"{f"({team["won"]}/{team["draw"]}/{team["lost"]})":<10}"
                f"{team["points"]:<3}"
            )

        return standings

    @commands.hybrid_command(
        name="standings",
        description="Displays the Serie A standings.",
        aliases=["table"],
    )
    async def standings(self, ctx: commands.Context):
        standings = await self.get_standings()
        headers = "#   Team        (W/D/L)   Pts"
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Serie A 25/26 Standings",
            description=f"```{headers}\n{standings}```",
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name} • Provided by CalcioBot"
        )
        await ctx.reply(
            embed=embed,
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(Standings(bot))
