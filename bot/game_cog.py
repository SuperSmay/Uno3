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
        if ctx.channel_id in current_games:
            try:
                current_games[ctx.channel_id].create_player(ctx.author.id)
                await ctx.respond(embed=discord.Embed(description="You joined the game!", color=SUCCESS_COLOR), delete_after=5)
            except ValueError as error:
                await ctx.respond(embed=discord.Embed(description="You are already in this game!", color=ERROR_COLOR), delete_after=5)
            except OutOfCardsError as error:
                await ctx.respond(embed=discord.Embed(description="There aren't enough cards to add another player!", color=ERROR_COLOR), delete_after=5)
        else:
            create_command = self.bot.get_application_command("create_game")
            response_string = "There isn't a game in this channel yet!"
            if create_command is not None:
                response_string += f" Create one with </create_game:{create_command.id}>"
            await ctx.respond(embed=discord.Embed(description=response_string, color=INFO_COLOR), delete_after=10)

    @commands.slash_command(name="create_game", description="Create a new game in this channel")
    async def create_game(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=game_support.create_game_embed(), view=game_support.CreateGameView())

    @commands.slash_command(name="lobby", description="Show the current game lobby")
    async def show_lobby(self, ctx: discord.ApplicationContext):
        await game_support.run_lobby_command(ctx)

    @commands.slash_command(name="start", description="Start the game when all players are ready")
    async def start_game(self, ctx: discord.ApplicationContext):
        if ctx.channel_id not in current_games:
            create_command = self.bot.get_application_command("create_game")
            response_string = "There isn't a game in this channel yet!"
            if create_command is not None:
                response_string += f" Create one with </{create_command.name}:{create_command.id}>"
            await ctx.respond(embed=discord.Embed(description=response_string, color=INFO_COLOR), delete_after=10)
            return
        
        game = current_games[ctx.channel_id]
        embed_response = discord.Embed(description="An error occurred", color=ERROR_COLOR)
        try:
            game.start_game()
            embed_response = discord.Embed(description="Game started!", color=SUCCESS_COLOR)
        except OutOfTurnError:
            embed_response = discord.Embed(description="The game already started!", color=ERROR_COLOR)
        await ctx.respond(embed=embed_response)

    @commands.slash_command(name="hand", description="Privately look at your hand")
    async def show_hand(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=game_support.hand_embed(ctx), view=game_support.HandView(ctx) , ephemeral=True)
            






def setup(bot: discord.Bot):
    bot.add_cog(GameCog(bot))