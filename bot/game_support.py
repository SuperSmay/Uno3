import discord
from discord.interactions import Interaction
from bot.global_variables import *
from bot.global_game_info import current_games
from unogame.card import Card
from unogame.game import UnoGame, UnoStates
from unogame.player import Player

def create_game_embed() -> discord.Embed:
    embed = discord.Embed(title="New game", description="Create a new game in this channel.", color=INFO_COLOR)
    return embed

def lobby_embed(ctx: discord.ApplicationContext) -> discord.Embed:

    if ctx.channel_id not in current_games:
        return discord.Embed(description="There is not a game in this channel yet!")
    
    game = current_games[ctx.channel_id]

    if game.state == UnoStates.PREGAME:
        embed = discord.Embed(title=f"<#{ctx.channel_id}> lobby")
        embed.add_field(name="Players:", value="\n".join([f"<@{player.player_id}>" for player in game.players]))
        return embed
    else:
        return game_status_embed(ctx)

    
def game_status_embed(ctx: discord.ApplicationContext) -> discord.Embed:

    if ctx.channel_id not in current_games:
        return discord.Embed(description="There is not a game in this channel yet!")

    game = current_games[ctx.channel_id]
    embed = discord.Embed(title=f"Game in <#{ctx.channel_id}>", color=game.deck.top_card.get_color_code())

    def turn_annotation(i):

        player: Player = game.players[i]
        player_line = f"<@{player.player_id}> - Cards: {len(player.hand)}"

        if i == game.turn_index:
            return f"__{player_line}__ {'↓' if not game.reversed else '↑'}"
        else:
            return player_line
            
    annotated_player_list = [turn_annotation(i) for i in range(len(game.players))]

    embed.add_field(name="Players:", value="\n".join(annotated_player_list), inline=False)
    embed.add_field(name="Game", value=(f"{game.status_message}\nIt's <@{game.players[game.turn_index].player_id}>'s turn" % game.status_players), inline=False)
    embed.set_thumbnail(url=game.deck.top_card.get_image_url())

    return embed
    
def hand_embed(ctx: discord.ApplicationContext | discord.Interaction) -> discord.Embed:
    if ctx.channel_id not in current_games:
        return discord.Embed(description="There is not a game in this channel yet!")
    
    if ctx.user is None:
        return discord.Embed(description="An error occurred", color=ERROR_COLOR)

    game = current_games[ctx.channel_id]
    try:
        player = game.get_player(ctx.user.id)
        embed = discord.Embed(title=f"Your hand")
        embed.add_field(name="Cards", value=", ".join([card.get_emoji_mention() for card in player.hand]))
        return embed
    except ValueError:
        return discord.Embed(description="You aren't in the game!", color=ERROR_COLOR)
    
class HandView(discord.ui.View):
    def __init__(self, ctx: discord.ApplicationContext | discord.Interaction):
        super().__init__()

        if ctx.channel_id not in current_games:
            return None
        
        if ctx.user is None:
            return None

        game = current_games[ctx.channel_id]
        try:
            player = game.get_player(ctx.user.id)
            self.add_item(self.HandDropdown(game, player))
            
        except ValueError:
            return None


    class HandDropdown(discord.ui.Select):
        def __init__(self, game: UnoGame, player: Player):
            options = [discord.SelectOption(label=str(card), emoji=card.get_emoji_mention()) for card in player.hand]
            super().__init__(
                placeholder="Choose a card to play...",
                min_values=1,
                max_values=1,
                options=options
            )
            self.player = player
            self.game = game

        async def callback(self, interaction: discord.Interaction):

            await interaction.response.send_message(
                f"You picked {self.values[0]}"
            )
            await self.view.message.edit(embed=hand_embed(interaction), view=HandView(interaction))
    

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