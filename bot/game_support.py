import discord
from discord.interactions import Interaction
from bot.global_variables import *
from bot.global_game_info import current_games
from unogame.card import Card
from unogame.game import MustPlayCardError, OutOfTurnError, UnoGame, UnoStates
from unogame.player import Player


async def run_lobby_command(ctx: discord.ApplicationContext):

    if ctx.channel_id not in current_games:
        await ctx.respond(embed=discord.Embed(description="There is not a game in this channel yet!"))
        return
    
    game = current_games[ctx.channel_id]

    response_embed = discord.Embed(description="An error occurred", color=ERROR_COLOR)

    if game.state == UnoStates.PREGAME:
        embed = discord.Embed(title=f"<#{ctx.channel_id}> lobby")
        embed.add_field(name="Players:", value="\n".join([f"<@{player.player_id}>" for player in game.players]))
        response_embed = embed
        
    else:
        response_embed = game_status_embed(ctx)


    sent_message = await ctx.response.send_message(embed=response_embed)

    game.lobby_message_id = (await sent_message.original_response()).id



def create_game_embed() -> discord.Embed:
    embed = discord.Embed(title="New game", description="Create a new game in this channel.", color=INFO_COLOR)
    return embed
    
def game_status_embed(ctx: discord.ApplicationContext | discord.Interaction) -> discord.Embed:

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
            self.add_item(self.HandButton(game, player))
            
        except ValueError:
            return None
        
    class HandButton(discord.ui.Button):
        def __init__(self, game: UnoGame, player: Player):
            super().__init__(label="Draw", emoji=Card.BACK_EMOJI)
            self.game = game
            self.player = player

        async def refresh_hand(self, interaction: discord.Interaction):
            if self.view is not None:
                await self.view.message.delete()
            await interaction.response.send_message(embed=hand_embed(interaction), view=HandView(interaction), ephemeral=True)

        async def refresh_lobby(self, interaction: discord.Interaction):
            lobby_message_id = self.game.lobby_message_id
            if lobby_message_id is not None:
                message = await interaction.channel.fetch_message(lobby_message_id)  # type: ignore - pylance channel type issue
                await message.edit(embed=game_status_embed(interaction))
            else:
                message = await interaction.channel.send(embed=game_status_embed(interaction))  # type: ignore - pylance channel type issue
                self.game.lobby_message_id = message.id

        async def callback(self, interaction: Interaction):
            try:
                self.game.draw_card_move(self.player)
                await self.refresh_hand(interaction)
                await self.refresh_lobby(interaction)
                await interaction.followup.send(f"You drew cards", ephemeral=True, delete_after=5)  # type: ignore - pylance overload issue
                

            except MustPlayCardError:
                await interaction.followup.send("You need to play a card", ephemeral=True, delete_after=5)  # type: ignore - pylance overload issue

            except OutOfTurnError:
                await interaction.followup.send("It's not your turn", ephemeral=True, delete_after=5)  # type: ignore - pylance overload issue


    class HandDropdown(discord.ui.Select):
        def __init__(self, game: UnoGame, player: Player):
            hand_no_duplicates = []
            for card in player.hand:
                if card not in hand_no_duplicates:
                    hand_no_duplicates.append(card)

            options = [discord.SelectOption(label=str(card), emoji=card.get_emoji_mention()) for card in hand_no_duplicates]
            
            super().__init__(
                placeholder="Choose a card to play...",
                min_values=1,
                max_values=1,
                options=options
            )
            self.player = player
            self.game = game

        async def refresh_hand(self, interaction: discord.Interaction):
            if self.view is not None:
                await self.view.message.delete()
            await interaction.response.send_message(embed=hand_embed(interaction), view=HandView(interaction), ephemeral=True)

        async def refresh_lobby(self, interaction: discord.Interaction):
            lobby_message_id = self.game.lobby_message_id
            if lobby_message_id is not None:
                message = await interaction.channel.fetch_message(lobby_message_id)  # type: ignore - pylance channel type issue
                await message.edit(embed=game_status_embed(interaction))
            else:
                message = await interaction.channel.send(embed=game_status_embed(interaction))  # type: ignore - pylance channel type issue
                self.game.lobby_message_id = message.id


        async def callback(self, interaction: discord.Interaction):
            card_chosen = Card.from_string(self.values[0])
            try:
                self.game.play_card_move(self.player, card_chosen)
                await self.refresh_hand(interaction)
                await self.refresh_lobby(interaction)
                await interaction.followup.send(f"You played {str(card_chosen)}", ephemeral=True, delete_after=5)  # type: ignore - pylance overload issue
                

            except:
                await self.refresh_hand(interaction)
                await interaction.followup.send("You can't play that right now!", ephemeral=True, delete_after=5)  # type: ignore - pylance overload issue
            
            
    

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