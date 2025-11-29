import discord
from discord.ext import commands
from fotmob import FotMob
import datetime

KNOCK_OUTS = {
    "final": "Final",
    "1/2": "Semi-final",
    "1/4": "Quarter-final",
    "1/8": "Round of 16",
}


class Matches(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.fotmob = FotMob()

    async def get_club_id(self, club):
        club = await self.fotmob.search_team(club)
        return club[0]["id"]

    async def get_next_fixture(self, club_id):
        match = await self.fotmob.get_team_next_fixture(club_id)
        return match

    async def get_previous_fixture(self, club_id):
        match = await self.fotmob.get_team_last_fixture(club_id)
        return match

    @commands.hybrid_command(
        name="nextmatch",
        description="Shows info about an upcoming fixture for a team",
        aliases=["next", "nextfixture"],
    )
    async def nextmatch(self, ctx: commands.Context, *, club):
        club_id = await self.get_club_id(club)
        match = await self.get_next_fixture(club_id)
        match_details = await self.fotmob.get_match_details(match["id"])
        tournament = match_details["general"]["leagueName"].replace("Final Stage", "")
        match_details = match_details["content"]["matchFacts"]["infoBox"]
        time = datetime.datetime.fromisoformat(match["status"]["utcTime"]).timestamp()
        stadium = match_details["Stadium"]["name"]

        matchday = (
            match_details["Tournament"]["round"]
            if match_details["Tournament"]["round"]
            else ""
        )

        if match_details["Referee"]:
            referee = (
                match_details["Referee"]["text"]
                if match_details["Referee"]["text"]
                else "Not Available"
            )
        else:
            referee = "Not Available"

        leg = (
            [match_details["legInfo"]["bestOfNum"], match_details["legInfo"]["bestOf"]]
            if match_details["legInfo"]
            else None
        )

        embed = discord.Embed(
            color=discord.Color.blue(),
            title=f"{match["home"]["name"]} vs {match["away"]["name"]}",
            description=f"""
:calendar_spiral: Kick-off: <t:{str(time)[:-2]}:f> - <t:{str(time)[:-2]}:R>
:stadium: Venue: {stadium}
<:whistle:1443317648052977666> Referee: {referee}""",
        )

        embed.set_author(
            name=f"{tournament} {f"{KNOCK_OUTS.get(matchday) if KNOCK_OUTS.get(matchday) else f"(Matchday {matchday})"}"} {f"(Leg {leg[0]} of {leg[1]})" if leg else ""}",
            icon_url=self.fotmob.get_league_logo(match["tournament"]["leagueId"]),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author.display_name} • Provided by CalcioBot"
        )

        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="lastmatch",
        description="Shows info about the previous fixture for a team",
        aliases=["last", "lastfixture", "previous", "prev"],
    )
    async def lastmatch(self, ctx: commands.Context, *, club):
        club_id = await self.get_club_id(club)
        match = await self.get_previous_fixture(club_id)
        match_details = await self.fotmob.get_match_details(match["id"])
        tournament = match_details["general"]["leagueName"].replace("Final Stage", "")
        match_details = match_details["content"]["matchFacts"]["infoBox"]
        time = datetime.datetime.fromisoformat(match["status"]["utcTime"]).timestamp()
        stadium = match_details["Stadium"]["name"]

        matchday = (
            match_details["Tournament"]["round"]
            if (
                match_details["Tournament"]["round"]
                and not match_details["Tournament"]["round"].replace(" ", "").isalpha()
            )
            else ""
        )

        if match_details["Referee"]:
            referee = (
                match_details["Referee"]["text"]
                if match_details["Referee"]["text"]
                else "Not Available"
            )
        else:
            referee = "Not Available"

        leg = (
            [match_details["legInfo"]["bestOfNum"], match_details["legInfo"]["bestOf"]]
            if match_details["legInfo"]
            else None
        )

        embed = discord.Embed(
            color=discord.Color.blue(),
            title=f"{match["home"]["name"]} {match["home"]["score"]} - {match["away"]["score"]} {match["away"]["name"]}",
            description=f"""
:calendar_spiral: Kick-off: <t:{str(time)[:-2]}:f> - <t:{str(time)[:-2]}:R>
:stadium: Venue: {stadium}
<:whistle:1443317648052977666> Referee: {referee}""",
        )

        embed.set_author(
            name=f"{tournament} {f"(Matchday {matchday})" if matchday.isdigit() else ""} {f"(Leg {leg[0]} of {leg[1]})" if leg else ""}",
            icon_url=self.fotmob.get_league_logo(match["tournament"]["leagueId"]),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author.display_name} • Provided by CalcioBot"
        )

        view = discord.ui.View()

        button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Lineups",
            url=f"https://fotmob.com{match["pageUrl"]}:tab=lineup",
        )
        view.add_item(item=button)

        button = discord.ui.Button(
            style=discord.ButtonStyle.link,
            label="Statistics",
            url=f"https://fotmob.com{match["pageUrl"]}:tab=stats",
        )
        view.add_item(item=button)

        await ctx.reply(embed=embed, view=view, mention_author=False)


async def setup(bot):
    await bot.add_cog(Matches(bot))
