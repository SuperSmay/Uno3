from __future__ import annotations # type: ignore (pylance shadow stdlib issues)
from unogame.card import Card

class Player:

    def __init__(self, player_id: int) -> None:

        self.player_id = player_id
        self.hand: list[Card] = []

    
    def add_card_to_hand(self, card: Card):
        """
        Adds the provided card to hand

        Args:
            card (Card): The card to add

        Raises:
            TypeError: If the card provided is not a card
        """

        if type(card) != Card:
            raise TypeError(card)

        self.hand.append(card)

    def play_card(self, card: Card) -> bool:
        """
        Removes the card provided from the players hand.
        If `card.return_to_discard == False`, then this function will always return true and do nothing.

        Args:
            card (Card): The card to remove

        Returns:
            bool: True if the player had the card or `card.return_to_discard == False`, False otherwise
        """

        if not card.return_to_discard:
            return True

        if card not in self.hand:
            return False

        else:
            self.hand.remove(card)
            return True

    def has_card_to_play(self, top_card: Card) -> bool:
        """
        Determines if the player has a card that is a valid play on top of top_card

        Args:
            top_card (Card): The card being play on top of (Top card of the game)

        Returns:
            bool: True if the player has a valid card to play, False otherwise
        """
        for card in self.hand:
            if card.can_be_played(top_card):
                return True

        return False

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Player):
            return __o.player_id == self.player_id
        else:
            return False
        

        
        