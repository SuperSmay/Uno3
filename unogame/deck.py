from __future__ import annotations # type: ignore (pylance shadow stdlib issues)
from unogame.card import Card, CardColors, CardFaces

import random # type: ignore (pylance shadow stdlib issues)

class DeckManager:

    def __init__(self, deck_count: int = 1) -> None:
        """
        Represents a draw and discard pile. By default initializes with a standard deck loaded
        """

        if deck_count < 1:
            raise ValueError("Deck count must be 1 or more")

        self.draw_pile: list[Card] = []

        for _ in range(deck_count):
            self.draw_pile += self.create_deck()

        self.discard_pile: list[Card] = []

        self.top_card: Card = self.draw_starting_card()

    def create_deck(self) -> list[Card]:
        """
        Creates a new standard deck of Uno

        Returns:
            list[Card]: A list containing all cards in a standard Uno deck
        """
        colors = [CardColors.RED, CardColors.YELLOW, CardColors.GREEN, CardColors.BLUE]
        faces = [CardFaces.ZERO, CardFaces.ONE, CardFaces.ONE, CardFaces.TWO, CardFaces.TWO, CardFaces.THREE, CardFaces.THREE,
        CardFaces.FOUR, CardFaces.FOUR, CardFaces.FIVE, CardFaces.FIVE, CardFaces.SIX, CardFaces.SIX, CardFaces.SEVEN, CardFaces.SEVEN,
        CardFaces.EIGHT, CardFaces.EIGHT, CardFaces.NINE, CardFaces.NINE, CardFaces.SKIP, CardFaces.SKIP,
        CardFaces.REVERSE, CardFaces.REVERSE, CardFaces.PLUS_TWO, CardFaces.PLUS_TWO]
        
        cards = []
        for color in colors:
            for face in faces:
                cards.append(Card(color, face))
        count = 0
        while count < 4:
            cards.append(Card(CardColors.WILD, CardFaces.WILD))
            cards.append(Card(CardColors.WILD, CardFaces.PLUS_FOUR))
            count += 1

        return cards

    def draw_card(self) -> Card:
        """
        Draws a random card from the draw pile. Will reshuffle if needed

        Raises:
            IndexError: If the deck and discard pile are both empty

        Returns:
            Card: A random card from the draw pile
        """

        # If the draw pile is empty, add the discard pile back into the draw pile
        if self.draw_pile.__len__() == 0:
            self.draw_pile += self.discard_pile
            self.discard_pile = []

        # If we still have no cards to draw, then raise an index error
        if self.draw_pile.__len__() == 0:
            raise IndexError("No cards left to draw")

        index: int = random.randrange(0, self.draw_pile.__len__())
        return self.draw_pile.pop(index)

    def play_card(self, card: Card) -> None:
        """
        Sets the top card to the provided card and adds the previous top card to the discard pile.
        Does not check if the card played is valid in the context of an Uno game

        Args:
            card (Card): Card to play
        """
        # If the card is a "ghost card", such as a colored wild card, then don't return it
        if self.top_card.return_to_discard:
            self.discard_pile.append(self.top_card)
        self.top_card = card

    def draw_starting_card(self) -> Card:
        """
        Draws cards until a card that is a valid starting card (anything non wild) is drawn

        Returns:
            Card: _description_
        """
        card = self.draw_card()
        while card.color == CardColors.WILD:
            # Put the card back in the draw pile manually, because per Uno rules the card is returned to the deck
            self.draw_pile.append(card)
            card = self.draw_card()

        return card

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, DeckManager):
            return __o.draw_pile == self.draw_pile and __o.discard_pile == self.discard_pile
        else:
            return False

    def __len__(self) -> int:
        return self.draw_pile.__len__() + self.discard_pile.__len__()

class OutOfCardsError(Exception): pass