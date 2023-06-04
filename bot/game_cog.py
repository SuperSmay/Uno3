import discord
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui.item import Item

from unogame.game import OutOfTurnError, UnoGame, OutOfCardsError
from bot.global_game_info import current_games as current_games
from bot.global_variables import *
import bot.game_support as game_support

class GameCog(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot: discord.Bot = bot


    @commands.slash_command(name="join", description="Join a game in the current channel")
    async def join(self, ctx: discord.ApplicationContext):
        await game_support.run_join_command(ctx)

    @commands.slash_command(name="create_game", description="Create a new game in this channel")
    async def create_game(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=game_support.create_game_embed(), view=game_support.CreateGameView())

    @commands.slash_command(name="lobby", description="Show the current game lobby")
    async def show_lobby(self, ctx: discord.ApplicationContext):
        await game_support.run_lobby_command(ctx)

    @commands.slash_command(name="start", description="Start the game when all players are ready")
    async def start_game(self, ctx: discord.ApplicationContext):
        await game_support.run_start_game_command(ctx)

    @commands.slash_command(name="hand", description="Privately look at your hand")
    async def show_hand(self, ctx: discord.ApplicationContext):
        await game_support.run_hand_command(ctx.interaction)
            






def setup(bot: discord.Bot):
    bot.add_cog(GameCog(bot))