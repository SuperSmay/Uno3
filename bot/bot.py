import discord
from discord.ext import commands

bot = commands.Bot()

@bot.event
async def on_ready():
    if bot.user is None:
        return

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    async for guild in bot.fetch_guilds():
        print(guild.name)





