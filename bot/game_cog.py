import discord
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui.item import Item

from unogame.game import UnoGame, OutOfCardsError
from bot.global_game_info import current_games as current_games

class GameCog(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot: discord.Bot = bot


    @commands.slash_command(name="join", description="Join a game in the current channel")
    async def _(self, ctx: discord.ApplicationContext):
        if ctx.channel_id in current_games:
            try:
                current_games[ctx.channel_id].create_player(ctx.author.id)
                await ctx.respond("You joined the game!")
            except ValueError as error:
                await ctx.respond("You are already in this game")
            except OutOfCardsError as error:
                await ctx.respond("There aren't enough cards to add another player!")
        else:
            await ctx.respond("There is not a game in this channel. Create one first!", view=CreateGameView())


class CreateGameView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(self.CreateButton())




    class CreateButton(discord.ui.Button):
        def __init__(self):
            super().__init__(style=discord.ButtonStyle.primary, label="Create game")

        async def callback(self, interaction: Interaction):
            channel_id = interaction.channel_id
            user_id = interaction.user.id if interaction.user is not None else None
            if channel_id is None or user_id is None:
                await interaction.response.send_message("An error has occurred")
                return

            if channel_id in current_games:
                await interaction.response.send_message("There is already a game in this channel")
            else:
                new_game = UnoGame()
                current_games[channel_id] = new_game
                new_game.create_player(user_id)
                await interaction.response.send_message("You joined the game!")



def setup(bot: discord.Bot):
    bot.add_cog(GameCog(bot))