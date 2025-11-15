import discord
from discord.ext import commands
import aiohttp
import os


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.season = "25/26"
        self.BASE_URL = "https://tmkt-api-production.up.railway.app"
        self.BASE_TM_URL = "https://www.transfermarkt.com/player/profil/spieler"
        self.session = aiohttp.ClientSession()

    async def get_player_id(self, player: str):
        url = f"{self.BASE_URL}/players/search?query={player}"

        async with self.session.get(url) as response:
            player = await response.json()

        return player["results"][0]["id"] if player["results"] else None

    async def get_player_info(self, player_id: int):
        url = f"{self.BASE_URL}/players/{player_id}"

        async with self.session.get(url) as response:
            player_info = await response.json()

        if "results" in player_info:
            player_info = player_info["results"]["result"]

            info = {
                "name": player_info["name"],
                "age": player_info["age"],
                "nationality": player_info["nationality"],
                "position": player_info["position"],
                "club": {
                    "name": player_info["club"]["name"],
                    "logo": player_info["club"]["logo"],
                },
                "shirt_number": player_info["shirt_number"],
                "market_value": (
                    player_info["market_value"].replace(" ", "")
                    if player_info["market_value"]
                    else "Not Available"
                ),
                "image": player_info["profile_image"],
                "status": player_info["status"],
            }

            return info

        return None

    async def get_player_stats(self, player_id: int):
        url = f"{self.BASE_URL}/players/{player_id}/stats"

        async with self.session.get(url) as response:
            player_stats = await response.json()
            player_stats = player_stats["results"]["total"]

        info = await self.get_player_info(player_id)

        if info["position"] != "Goalkeeper":
            stats = {
                "appearances": player_stats["appearances"],
                "goals": player_stats["goals"],
                "assists": player_stats["assists"],
                "yellow_cards": player_stats["yellow_cards"],
                "second_yellow_cards": player_stats["second_yellow_cards"],
                "red_cards": player_stats["red_cards"],
            }

        else:
            stats = {
                "appearances": player_stats["appearances"],
                "goals_conceded": player_stats["red_cards"],
                "clean_sheets": player_stats["minutes_played"],
                "goals/assists": f"{player_stats["goals"]}/{player_stats["assists"]}",
                "yellow_cards": player_stats["yellow_cards"],
                "red_cards": player_stats["second_yellow_cards"],
            }

        return stats

    @commands.hybrid_command(
        name="player",
        description="Displays the information and statistics of a football player",
    )
    async def player(self, ctx: commands.Context, *, player):
        player_id = (
            await self.get_player_id(player) if not player.isdigit() else int(player)
        )
        info = await self.get_player_info(player_id)

        if player_id and info:
            stats = await self.get_player_stats(player_id)
            embed = discord.Embed(
                description=f"{info["name"]} {f"({info["age"]})" if info["status"] != "deceased" else ""} Information and {self.season if info["status"] != "retired" and info["status"] != "deceased" else "All-Time"} Statistics",
                color=discord.Color.blue(),
            )

            embed.set_author(
                name=(
                    (
                        f"{info["club"]["name"]} #{info["shirt_number"]}: {info["name"]}"
                        if info["club"]["name"] != "Retired"
                        else f"Retired: {info["name"]}"
                    )
                    if info["status"] != "deceased"
                    else info["name"]
                ),
                url=f"{self.BASE_TM_URL}/{player_id}",
                icon_url=(
                    (
                        f"{info["club"]["logo"]}"
                        if info["club"]["name"] != "Retired"
                        else "https://tmssl.akamaized.net//images/wappen/normquad/123.png"
                    )
                    if info["status"] != "deceased"
                    else "https://tmssl.akamaized.net//images/wappen/small/4023.png"
                ),
            )

            embed.set_thumbnail(url=info["image"])

            embed.add_field(name="Nationality:", value=info["nationality"], inline=True)
            embed.add_field(name="Position:", value=info["position"], inline=True)
            embed.add_field(
                name="Market Value:", value=(info["market_value"]), inline=True
            )

            for name, value in stats.items():
                embed.add_field(
                    name=f"{name.title().replace("_", " ")}:",
                    value=value.replace("-", "0"),
                    inline=True,
                )

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name} • Provided by Transfermarkt and CalcioBot",
                icon_url="https://www.transfermarkt.com/android-chrome-192x192.png",
            )

            return await ctx.reply(embed=embed, mention_author=False)

        else:
            embed = discord.Embed(
                color=discord.Color.red(),
                title=":warning: Error: Player Not Found",
                description=f'```We couldn\'t find any player with the name/ID "{player}"\n'
                "Check the spelling or try a different name```",
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name} • Provided by CalcioBot"
            )

            return await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(Player(bot))
