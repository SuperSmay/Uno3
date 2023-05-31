from __future__ import annotations # type: ignore (pylance shadow stdlib issues)

from unogame.card import Card, CardColors, CardFaces
from unogame.deck import DeckManager, OutOfCardsError
from unogame.player import Player

from dataclasses import dataclass # type: ignore (pylance shadow stdlib issues)
from enum import Enum # type: ignore (pylance shadow stdlib issues)

class UnoGame:

    def __init__(self, ruleset: UnoRules | None = None) -> None:

        self.ruleset = ruleset if ruleset is not None else UnoRules()

        self.players: list[Player] = []
        self.deck = DeckManager(self.ruleset.number_of_decks)

        self.turn_index = 0
        self.current_stack = 0
        self.reversed = False
        self.state = UnoStates.PREGAME

        # Status message stuff
        self.status_message = "Waiting to start..."
        self.status_players = ()
        # Discord interaction stuff
        self.lobby_message_id: int | None = None

    def create_player(self, player_id: int) -> None:
        """
        Creates a player with the provided id, then draws them a hand and adds them to the game 

        Args:
            player_id (int): The player_id to add

        Raises:
            ValueError: If the player_id is already the id of a player in this game
            OutOfCardsError: If there are not enough cards left to add another player
        """

        # If the ID is already used, throw an error
        if (player_id in [player.player_id for player in self.players]):
            raise ValueError(f"player_id {player_id} already in use")

        # If there aren't enough cards for another player, raise an error
        if len(self.deck) < self.ruleset.starting_hand_size:
            raise OutOfCardsError

        # Create player
        new_player = Player(player_id)

        # Draw player a hand
        for _ in range(self.ruleset.starting_hand_size):
            card = self.deck.draw_card()
            new_player.add_card_to_hand(card)

        # Add them to the list
        self.players.append(new_player)


    def remove_player(self, player_id: int) -> None:
        """
        Removes the provided player_id from the game and returns all their cards to the discard pile

        Args:
            player_id (int): The id of the player to remove

        Raises:
            ValueError: If the player_id is not the id of a player in this game
        """

        # Get the index of the player (Let ValueError propagate)
        index = self.players.index(Player(player_id))

        # Get the actual player in the game
        player = self.players[index]

        # Put all the cards back in the deck (don't need to bother removing them from the hand because its about to get deleted)
        for card in player.hand:
            self.deck.play_card(card)

        # Add them to the list
        self.players.pop(index)

    def get_player(self, player_id: int) -> Player:
        """
        Get the player by id

        Args:
            player_id (int): The id to get

        Raises:
            ValueError: If the player is not in the game

        Returns:
           Player: The player with the given id
        """
        index = self.players.index(Player(player_id))
        return self.players[index]

    def play_card_move(self, player: Player, card: Card, allow_mismatch_play: bool = False) -> None:
        """
        Has the player given play the card given from their hand,
        and will update game state accordingly

        Args:
            player (Player): The player who plays a card
            card (Card): The card they are playing
            allow_mismatch_play (bool): If True, any card will count as a valid card to play on top of the top card. Only affects standard play, not jump-ins 

        Raises:
            OutOfTurnError: If the move was made out of turn (or an invalid jump-in card was attempted to be played)
            InvalidCardPlayedError: It is that player's turn, but the card they played was an invalid move
            PlayerDoesNotHaveCardError: The play was valid, but the player did not have the card they attempted to play
        """
        # Can't play a card before the game starts or after someone won
        if self.state == UnoStates.PREGAME or self.state == UnoStates.PLAYER_WON:
            raise OutOfTurnError

        # Can't play a card during a seven/zero if the rules are set to not allow jump-ins during those
        # This is only to stop jump-ins during those cases
        elif self.state == UnoStates.WAITING_FOR_PICK_PLAYER_TO_SWAP and not self.ruleset.jump_in_during_seven:
            raise OutOfTurnError
        elif self.state == UnoStates.WAITING_FOR_CHOOSE_TO_ROTATE and not self.ruleset.jump_in_during_zero:
            raise OutOfTurnError

        # If the game is waiting for the next move and the player who just tried to make a move was the current turn,
        # then process the play
        elif ((self.state == UnoStates.WAITING_FOR_PLAY or self.state == UnoStates.WAITING_FOR_DRAW_RESPONSE) and 
                self.players[self.turn_index] == player):
            # Check if the card is valid in the first place
            if not card.can_be_played(self.deck.top_card) and not allow_mismatch_play:
                raise InvalidCardPlayedError
            
            # Remove the card from the player
            if not player.play_card(card):
                raise PlayerDoesNotHaveCardError

            self.deck.play_card(card)

            # Check if the player who just played a card ran out of cards and won
            if len(player.hand) == 0:
                self.state = UnoStates.PLAYER_WON

            self._process_card_state_changes(player, card)

        elif (self.state == UnoStates.WAITING_FOR_PLUS_RESPONSE):
            # If the card is a plus card that can be stacked, then the card is added to the stack and play continues
            # Keep in mind the various rules for stacking plus_twos on plus_fours

            # Case stacking is off
            if not self.ruleset.stacking:
                raise InvalidCardPlayedError("Stacking is disabled")

            # Case standard stack
            elif self.deck.top_card.face == card.face:
                # The card can be played as normal

                # Update the state so play_card_move will process it
                self.state = UnoStates.WAITING_FOR_PLAY

                self.play_card_move(player, card)

            # Case plus fours can be stacked on plus twos
            elif (self.ruleset.stack_plus_fours_on_plus_twos and
                    self.deck.top_card.face == CardFaces.PLUS_TWO and 
                    card.face == CardFaces.PLUS_FOUR):
                # The card can be played as normal

                # Update the state so play_card_move will process it
                self.state = UnoStates.WAITING_FOR_PLAY

                self.play_card_move(player, card)

            # Case plus twos can always be stacked on plus fours
            elif (self.ruleset.stack_all_plus_twos_on_plus_fours and 
                    self.deck.top_card.face == CardFaces.PLUS_FOUR and 
                    card.face == CardFaces.PLUS_TWO):
                # The card can be played as normal

                # Update the state so play_card_move will process it
                self.state = UnoStates.WAITING_FOR_PLAY

                # We must bypass restrictions in this case, because the plus two may not normally be a valid move
                self.play_card_move(player, card, True)

            # Case only color matched plus twos can be stacked on plus fours
            elif (self.ruleset.stack_color_matching_plus_twos_on_plus_fours and 
                    self.deck.top_card.face == CardFaces.PLUS_FOUR and 
                    card.face == CardFaces.PLUS_TWO and
                    self.deck.top_card.color == card.color):
                # The card can be played as normal

                # Update the state so play_card_move will process it
                self.state = UnoStates.WAITING_FOR_PLAY

                self.play_card_move(player, card)


            # If the card is anything else, thats an InvalidCardPlayedError
            else:
                raise InvalidCardPlayedError

        # Otherwise, if the card is a jump-in (and the jump-in rule is enabled), then its always* valid
        # *not valid if the game hasn't started, or depending on jump_in_during_seven/zero rules
        elif card.can_be_jumped_in(self.deck.top_card) and self.ruleset.jump_ins:
            # Do the jump-in stuff
            # Start by updating turn_index to the index of whoever jumped in
            self.turn_index = self.players.index(player)
            # Then proceed normally

            # Remove the card from the player
            if not player.play_card(card):
                raise PlayerDoesNotHaveCardError

            # Return card to deck
            self.deck.play_card(card)

            # Check if the player who just played a card ran out of cards and won
            if len(player.hand) == 0:
                self.state = UnoStates.PLAYER_WON

            # Important: we must check if the card could be a stack card and jump-in stacking is disabled here,
            # as process_standard_card_play does not clear a stack in that case
            if not self.ruleset.jump_ins_stack and (card.face == CardFaces.PLUS_FOUR or card.face == CardFaces.PLUS_TWO):
                # Reset the stack if jump-ins are supposed to clear the stack
                self.current_stack = 0


            self._process_card_state_changes(player, card)
        
        # If we still haven't hit a valid case for playing a card, then raise an error, as the play wasn't valid
        else:
            raise OutOfTurnError

    def draw_card_move(self, player: Player) -> None:
        """
        The given player draws a card, or as many cards as needed to obtain a playable card,
        based on ruleset.draw_until_can_play.
        This is also used to accept drawing cards from a single plus card or a stack.
        If the deck runs out of cards during drawing, then drawing is ended, and play continues

        Args:
            player (Player): The player drawing cards

        Raises:
            OutOfTurnError: If it is not the player's turn, or drawing a card is not a valid option
            MustPlayCardError: If forceplay is on and the player can play a card
        """

        # Make sure its this player's turn
        if self.turn_index != self.players.index(player):
            raise OutOfTurnError

        # If we're waiting for a player to accept drawing cards, then they should draw those cards here
        elif self.state == UnoStates.WAITING_FOR_PLUS_RESPONSE:
            for _ in range(self.current_stack):
                try:
                    player.add_card_to_hand(self.deck.draw_card())
                # If the deck somehow runs out of cards, then cancel drawing more
                except OutOfCardsError:
                    break

            # Reset the stack and increment the turn
            self.current_stack = 0
            self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)
            self.state = UnoStates.WAITING_FOR_PLAY

        # Make sure we're waiting for them to play a card
        elif self.state != UnoStates.WAITING_FOR_PLAY:
            raise OutOfTurnError

        # Make sure that force play is not on, or if it is make sure they don't have a card to play
        elif self.ruleset.force_play and player.has_card_to_play(self.deck.top_card):
            raise MustPlayCardError

        # Now we know that this was a valid move and just a general draw attempt
        else:
            # They will always draw at least one card
            player.add_card_to_hand(self.deck.draw_card())
            
            # but if draw_until_can_play is on, then they might need to keep going
            if self.ruleset.draw_until_can_play:
                while not player.has_card_to_play(self.deck.top_card):
                    try:
                        player.add_card_to_hand(self.deck.draw_card())
                    # If somehow the deck ran out of cards, than just cancel the drawing (This case will need to handled by other functions
                    # that expect the player to be able to play)
                    except OutOfCardsError:
                        break

                # Wait to see what they want to do with the last card they drew
                self.state = UnoStates.WAITING_FOR_DRAW_RESPONSE
            # In draw one mode, the turn is automatically passed to the next player
            else:
                self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)
                self.state = UnoStates.WAITING_FOR_PLAY

    def pass_turn_move(self, player: Player) -> None:
        """
        This is ONLY valid when the deck is out of cards and the player has no cards that are valid plays,
        OR when they have just drawn cards and force_play is off.
        It also must be this player's turn.

        Args:
            player (Player): The player passing their turn

        Raises:
            OutOfTurnError: If it is not valid for that player to pass
        """
        if self.players[self.turn_index] != player:
            raise OutOfTurnError("Not this player's turn")

        if self.state != UnoStates.WAITING_FOR_PLAY and self.state != UnoStates.WAITING_FOR_DRAW_RESPONSE:
            raise OutOfTurnError("Not valid time to pass turn")

        # First case where this is valid, forceplay is off and the player just drew cards
        if self.state == UnoStates.WAITING_FOR_DRAW_RESPONSE and not self.ruleset.force_play:
            # If this happens, we can safely skip the other checks
            pass

        elif len(self.deck) > 0:
            raise OutOfTurnError("There are still cards left to draw")

        elif player.has_card_to_play(self.deck.top_card):
            raise OutOfTurnError("Player has at least one valid play")

        # If all checks are passes, then this is allowed
        self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)
        self.state = UnoStates.WAITING_FOR_PLAY

    def choose_color_move(self, player: Player, color: CardColors) -> None:
        """
        The given player chooses a color for a wild card.

        Args:
            player (Player): The player picking the color
            color (CardColors): The color chosen. Cannot be WILD

        Raises:
            OutOfTurnError: If the game is not waiting for the given player to choose a color
            InvalidCardPlayedError: If the color given is WILD
        """

        # If we aren't waiting for a color or it isn't this player's turn
        if self.state != UnoStates.WAITING_FOR_WILD_COLOR or self.players[self.turn_index] != player:
            raise OutOfTurnError
        
        if color == CardColors.WILD:
            raise InvalidCardPlayedError("Must choose a color that isn't wild")
        
        card = Card(color, self.deck.top_card.face)
        # This is a temp card to show the color and do potential plus card processing. Do not store it in discard pile
        card.return_to_discard = False
        # Change state so play_card_move will process it
        self.state = UnoStates.WAITING_FOR_PLAY
        self.play_card_move(player, card)

    def _process_card_state_changes(self, player: Player, card: Card):
        """
        Processes the state change after a card is played normally.
        Sets state to WAITING_FOR_WILD_COLOR after a wild for example.
        Also processes skips, reverses, and plus cards


        Args:
            player (Player): The player that played the card
            card (Card): The card that was played
        """
        if card.color == CardColors.WILD:
            self.state = UnoStates.WAITING_FOR_WILD_COLOR
        elif card.face == CardFaces.PLUS_FOUR:
            self.current_stack += 4
            self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)
            self.state = UnoStates.WAITING_FOR_PLUS_RESPONSE
        elif card.face == CardFaces.PLUS_TWO:
            self.current_stack += 2
            self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)
            self.state = UnoStates.WAITING_FOR_PLUS_RESPONSE
        elif card.face == CardFaces.SKIP:
            self.turn_index = (self.turn_index + (2 if not self.reversed else -2)) % len(self.players)
            self.state = UnoStates.WAITING_FOR_PLAY
        elif card.face == CardFaces.REVERSE:
            self.reversed = not self.reversed
            if len(self.players) == 2:
                # Acts as a skip in 1v1 per Uno rules
                self.turn_index = (self.turn_index + (2 if not self.reversed else -2)) % len(self.players)
            else:
                self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)
            self.state = UnoStates.WAITING_FOR_PLAY
        elif card.face == CardFaces.ZERO and self.ruleset.zero_rotate_hands:
            self.state = UnoStates.WAITING_FOR_CHOOSE_TO_ROTATE
        elif card.face == CardFaces.SEVEN and self.ruleset.seven_swap_hands:
            self.state = UnoStates.WAITING_FOR_PICK_PLAYER_TO_SWAP
        else:
            self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)

    def seven_swap_move(self, player: Player, player_index: int):
        """
        Represents a player picking a another player to swap hands with.
        If `player_index` is that player's own index then they are picking nobody, may or may not be allowed based on current rules.

        Args:
            player (Player): The player picking
            player_index (int): The index of the picked player

        Raises:
            OutOfTurnError: If it is not this players turn or the game is not waiting for this
            ValueError: If the index is the index of the player making the move and force_seven_swap is on
            IndexError: The index is out of range 
        """

        # Can only do this while the game is waiting for someone to pick a player, and that player is the player provided
        if self.state != UnoStates.WAITING_FOR_PICK_PLAYER_TO_SWAP or self.players[self.turn_index] != player:
            raise OutOfTurnError
        
        # Can only pick yourself if force_seven_swap is False
        elif self.ruleset.force_seven_swap and self.players[player_index] == player:
            raise ValueError("Index must not be the index of player")

        # Index obviously needs to be in the list of players
        elif player_index < 0 or player_index >= len(self.players):
            raise IndexError("Index must be a valid index in self.players")

        # Also if this somehow happens with only one player, then move on
        elif len(self.players) < 2:
            pass

        # Now that we know this is valid, do the thing
        else:
            temp = player.hand
            player.hand = self.players[player_index].hand
            self.players[player_index].hand = temp

        self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)
        self.state = UnoStates.WAITING_FOR_PLAY

    def zero_rotate_move(self, player: Player, choose_to_rotate: bool):
        """
        Represents a player choosing to rotate all hands or not.
        If `choose_to_rotate` is False, the rotate will not happen. This may or may not be valid based on current rules.

        Args:
            player (Player): The player picking
            choose_to_rotate (bool): The choice of the player to rotate or not

        Raises:
            OutOfTurnError: If it is not this players turn or the game is not waiting for this
            ValueError: If the choice is False and force_zero_rotate is on
        """

        # Can only do this while the game is waiting for someone to pick a player, and that player is the player provided
        if self.state != UnoStates.WAITING_FOR_CHOOSE_TO_ROTATE or self.players[self.turn_index] != player:
            raise OutOfTurnError
        
        # Can only pick false if force_zero_rotate is False
        if self.ruleset.force_zero_rotate and not choose_to_rotate:
            raise ValueError("choose_to_rotate must be False because force_zero_rotate is on")

        # Now that we know this is valid, do the thing
        if choose_to_rotate:

            # If the number of players is one or less(???) then don't even try
            if len(self.players) < 2:
                pass
                
            # Reversed direction
            elif self.reversed:
                first_player_hand = self.players[0].hand

                for i in range(len(self.players) - 1):
                    self.players[i].hand = self.players[i+1].hand
                
                self.players[-1].hand = first_player_hand
                

            # Normal direction
            else:
                last_player_hand = self.players[-1].hand
                
                for i in range(len(self.players)-1, -1, -1):
                    self.players[i].hand = self.players[i-1].hand
                
                self.players[0].hand = last_player_hand

        self.turn_index = (self.turn_index + (1 if not self.reversed else -1)) % len(self.players)
        self.state = UnoStates.WAITING_FOR_PLAY


        

    def start_game(self):
        """
        Starts the game

        Raises:
            OutOfTurnError: If the game has already started
        """
        if self.state != UnoStates.PREGAME:
            raise OutOfTurnError
        
        self.state = UnoStates.WAITING_FOR_PLAY



@dataclass
class UnoRules:
    starting_hand_size = 7
    number_of_decks = 1
    jump_ins = False

    stacking = False
    # Stacking rules
    jump_ins_stack = False
    stack_plus_fours_on_plus_twos = False
    stack_all_plus_twos_on_plus_fours = False
    stack_color_matching_plus_twos_on_plus_fours = False
    
    force_play = True
    draw_until_can_play = True

    # 7-0
    seven_swap_hands = False
    force_seven_swap = False
    zero_rotate_hands = False
    force_zero_rotate = False
    jump_in_during_seven = False
    jump_in_during_zero = False

class UnoStates(Enum):
    PREGAME = 0
    WAITING_FOR_PLAY = 1
    WAITING_FOR_PLUS_RESPONSE = 2
    WAITING_FOR_WILD_COLOR = 3
    WAITING_FOR_PICK_PLAYER_TO_SWAP = 4
    WAITING_FOR_CHOOSE_TO_ROTATE = 5
    WAITING_FOR_DRAW_RESPONSE = 6
    PLAYER_WON = 7

class OutOfTurnError(Exception): pass
class PlayerDoesNotHaveCardError(Exception): pass
class InvalidCardPlayedError(Exception): pass
class MustPlayCardError(Exception): pass