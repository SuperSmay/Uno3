import discord
from discord.ext import commands

import dotenv
from pathlib import Path # type: ignore (pylance shadow stdlib issues)

config = dotenv.dotenv_values(Path('storage/.env'))

bot = commands.Bot()
bot.load_extension("bot.info_cog")

if str(config["DEV_MODE"]).lower() == "true":
    bot.debug_guilds = [764385563289452545]

@bot.event
async def on_ready():
    if bot.user is None:
        return

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    async for guild in bot.fetch_guilds():
        print(guild.name)



@bot.slash_command(name="hello")
async def hello_world(ctx: discord.ApplicationContext):
    await ctx.respond("Hi there")

