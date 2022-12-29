from __future__ import annotations # type: ignore (pylance shadow stdlib issues)
from enum import Enum # type: ignore

from unogame.card_image_dictionaries import card_emoji, card_images


class Card:

    def __init__(self, color: CardColors, face: CardFaces, return_to_discard: bool = True) -> None:
        self.color = color
        self.face = face
        self.return_to_discard = return_to_discard

    def get_emoji_mention(self) -> str:
        """
        Returns the mention for the emoji representing this card

        Returns:
            str: The discord emoji mention
        """

        face_string = str(self.face.value)
        color_string = str(self.color.value)

        card_name = f"{face_string}_{color_string}"

        return card_emoji[card_name]

    def get_image_url(self) -> str:
        """
        Returns the url for the image representing this card

        Returns:
            str: The image url
        """

        face_string = str(self.face.value)
        color_string = str(self.color.value)

        image_url = f"{face_string}_{color_string}"

        return card_images[image_url]

    def can_be_played(self, other_card: Card) -> bool:
        """
        Determines if this card can be played on top of other_card

        Args:
            other_card (Card): The card on the top of the pile

        Returns:
            bool: If the card can be played
        """
        # If this card is wild, then it can always be played
        if self.color == CardColors.WILD:
            return True
        # If the colors match, then we good
        if self.color == other_card.color:
            return True
        # If the faces match, then we good
        if self.face == other_card.face:
            return True

        # Otherwise, they don't match
        return False

    def can_be_jumped_in(self, other_card: Card) -> bool:
        """
        Determines if this card can be jumped in with on top of other_card

        Args:
            other_card (Card): The card on the top of the pile

        Returns:
            bool: If the card can be jumped in with
        """

        # If the colors and faces match, then we good
        if self.color == other_card.color and self.face == other_card.face:
            return True

        # If the card is wild and the face matches, then we good
        if (self.color == CardColors.WILD) and self.face == other_card.face:
            return True

        # Otherwise, they don't match
        return False

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Card):
            return __o.color == self.color and __o.face == self.face
        else:
            return False






class CardColors(Enum):
    GREEN = 'green'
    YELLOW = 'yellow'
    BLUE = 'blue'
    RED = 'red'
    WILD = 'black'

class CardFaces(Enum):
    ZERO = 'zero'
    ONE = 'one'
    TWO = 'two'
    THREE = 'three'
    FOUR = 'four'
    FIVE = 'five'
    SIX = 'six'
    SEVEN = 'seven'
    EIGHT = 'eight'
    NINE = 'nine'
    SKIP = 'skip'
    REVERSE = 'reverse'
    PLUS_TWO = 'plus_two'
    PLUS_FOUR = 'plus_four'
    WILD = 'wild'
