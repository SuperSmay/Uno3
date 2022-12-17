from __future__ import annotations # type: ignore (pylance shadow stdlib issues)
from enum import Enum # type: ignore

from unogame.card_image_dictionaries import card_emoji, card_images


class Card:

    def __init__(self, color: CardColors, face: CardFaces) -> None:
        self.color = color
        self.face = face

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
