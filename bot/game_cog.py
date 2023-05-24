import discord
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui.item import Item

from unogame.game import UnoGame, OutOfCardsError
from bot.global_game_info import current_games as current_games
from bot.global_variables import *

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
        await ctx.respond(embed=create_game_embed(), view=CreateGameView())

    @commands.slash_command(name="lobby", description="Show the current game lobby")
    async def show_lobby(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=lobby_embed(ctx))

def create_game_embed() -> discord.Embed:
    embed = discord.Embed(title="New game", description="Create a new game in this channel.", color=INFO_COLOR)
    return embed

def lobby_embed(ctx: discord.ApplicationContext) -> discord.Embed:

    if ctx.channel_id in current_games:

        game = current_games[ctx.channel_id]
        player_list = [ctx.bot.get_user(player.player_id) for player in game.players]

        embed = discord.Embed(title=f"<#{ctx.channel_id}> lobby")
        embed.add_field(name="Players:", value="\n".join([str(player.player_id) for player in game.players]))
        return embed
    
    else:
        return discord.Embed(description="There is not a game in this channel yet!")

class CreateGameView(discord.ui.View):
    def __init__(self):
        super().__init__()
   
    @discord.ui.button(label="Create", style=discord.ButtonStyle.primary)
    async def callback(self, button: discord.Button, interaction: Interaction):
        channel_id = interaction.channel_id
        user_id = interaction.user.id if interaction.user is not None else None
        if channel_id is None or user_id is None:
            await interaction.response.send_message(embed=discord.Embed(description="An error occurred", color=ERROR_COLOR), delete_after=5)
            return

        embed_response = discord.Embed(description="An error occurred", color=ERROR_COLOR)
        if channel_id in current_games:
            embed_response = discord.Embed(description="There is already a game in this channel", color=ERROR_COLOR)
        else:
            new_game = UnoGame()
            current_games[channel_id] = new_game
            embed_response = discord.Embed(description="New game created!", color=SUCCESS_COLOR)

        if interaction.message is not None:
            await interaction.message.edit(embed=embed_response, view=None)
        else:
            await interaction.response.send_message(embed=embed_response, delete_after=5)



def setup(bot: discord.Bot):
    bot.add_cog(GameCog(bot))