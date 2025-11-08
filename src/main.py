import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=",", intents=intents)


@bot.event
async def on_ready():
    print(
        f"{"-" * len(f"Bot is logged in as {bot.user}!")}\nBot is logged in as {bot.user}!\n{"-" * len(f"Bot is logged in as {bot.user}!")}"
    )
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="Watching Calcio"
        ),
    )


async def load_extensions():
    for root, dirs, files in os.walk("./src/cogs"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.relpath(root, "./src").replace(os.sep, ".")
                await bot.load_extension(f"{path}.{file[:-3]}")
                print(f"✅ Successfully loaded {path}.{file[:-3]}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.environ.get("BOT_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
