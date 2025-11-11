import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_standings():
    teams = []
    url = "https://api.football-data.org/v4/competitions/SA/standings"
    response = requests.get(
        url, headers={"X-Auth-Token": os.getenv("FOOTBALL_DATA_API_KEY")}
    )
    data = response.json()["standings"][0]["table"]

    for team in data:
        teams.append(
            {
                "position": team["position"],
                "name": team["team"]["shortName"],
                "played": team["playedGames"],  # correct field name
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


class Standings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="standings",
        description="Displays the Serie A standings.",
        aliases=["table"],
    )
    async def standings(self, ctx: commands.Context):
        headers = "#   Team        (W/D/L)   Pts"
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Serie A 25/26 Standings",
            description=f"```{headers}\n{get_standings()}```",
        )
        await ctx.reply(
            embed=embed,
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(Standings(bot))
