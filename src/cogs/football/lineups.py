import discord
from discord.ext import commands
from sofascore_wrapper.api import SofascoreAPI
from sofascore_wrapper.search import Search
from sofascore_wrapper.match import Match
from sofascore_wrapper.team import Team


class Lineups(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api = SofascoreAPI()

    async def get_team_id(self, team: str):
        team = await Search(self.api, search_string=team).search_teams()
        return team["results"][0]["entity"]["id"] if team["results"] else None

    async def get_next_fixture_id(self, team_id: int):
        match = await Team(self.api, team_id).next_fixtures()
        for i in range(1, len(match) + 1):
            if match[-i]["status"]["type"] == "notstarted":
                return match[-i]["id"]

    async def get_match_info(self, match_id: str):
        match = await Match(self.api, match_id).get_match()
        match = match["event"]

        home, away = (
            match["homeTeam"]["shortName"],
            match["awayTeam"]["shortName"],
        )

        try:
            home_lineup = await Match(self.api, match_id).lineups_home()
            away_lineup = await Match(self.api, match_id).lineups_away()
        except Exception:
            status, home_lineup, away_lineup = (
                "unavailable",
                "unavailable",
                "unavailable",
            )
        else:
            status = "ok"

        match = {
            "home_team": home,
            "away_team": away,
            "home_lineup": home_lineup,
            "away_lineup": away_lineup,
            "status": status,
        }

        return match

    @commands.hybrid_command(
        name="lineups",
        description="Displays the lineups of the next fixture of a team",
    )
    async def lineups(self, ctx: commands.Context, *, team):
        await ctx.defer()

        team_id = await self.get_team_id(team) if not team.isdigit() else int(team)
        match_id = await self.get_next_fixture_id(team_id)
        info = await self.get_match_info(match_id)

        if info["status"] != "ok" or not info["home_lineup"]["confirmed"]:
            return await ctx.reply(
                f"Lineups for {info['home_team']} vs {info['away_team']} are not yet available.",
                mention_author=False,
            )

        home_starters = info["home_lineup"].get("starters", [])
        away_starters = info["away_lineup"].get("starters", [])

        h_form = info["home_lineup"].get("formation", "")
        a_form = info["away_lineup"].get("formation", "")

        lineup_text = ""

        lineup_text += f"**{info['home_team']}** ({h_form})\n```text\n"
        for h in home_starters:
            p = h.get("player", {})
            name = p.get("shortName", "")

            if h.get("captain"):
                name += " (c)"
            num = p.get("jerseyNumber", "??")
            lineup_text += f"{num:>2}. {name}\n"
        lineup_text += "```\n"

        lineup_text += f"**{info['away_team']}** ({a_form})\n```text\n"
        for a in away_starters:
            p = a.get("player", {})
            name = p.get("shortName", "")
            if a.get("captain"):
                name += " (c)"
            num = p.get("jerseyNumber", "??")
            lineup_text += f"{num:>2}. {name}\n"
        lineup_text += "```"

        embed = discord.Embed(
            title=f"Lineups: {info['home_team']} vs {info['away_team']}",
            description=lineup_text,
            color=discord.Color.blue(),
        )

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Lineups(bot))
