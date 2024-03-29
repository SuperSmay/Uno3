from unogame.card import *

def test_constructor():
    """
    Tests that the constructor for Card works as expected

    Raises:
        AssertionError: If any of the tests fail
    """

    test_card = Card(CardColors.GREEN, CardFaces.REVERSE)

    assert test_card.color == CardColors.GREEN

    assert test_card.face == CardFaces.REVERSE


def test_get_emoji_mention():
    """
    Tests that Card.get_emoji_mention returns the correct emoji mention for a card

    Raises:
        AssertionError: If any of the tests fail
    """

    test_card = Card(CardColors.BLUE, CardFaces.PLUS_TWO)
    assert test_card.get_emoji_mention() == "<:plus2_blue:736430793815097416>"


def test_get_image_url():
    """
    Tests that Card.get_image_url returns the correct discord cdn image for a card

    Raises:
        AssertionError: If any of the tests fail
    """
    
    test_card = Card(CardColors.GREEN, CardFaces.FIVE)
    assert test_card.get_image_url() == "https://cdn.discordapp.com/attachments/742986384113008712/742986667438112869/Background_47.png"


def test_can_be_played():
    """
    Tests that Card.can_be_played returns the correct value

    Raises:
        AssertionError: If any of the tests fail
    """

    test_top_card = Card(CardColors.YELLOW, CardFaces.THREE)

    # Playable by color
    test_card_one = Card(CardColors.YELLOW, CardFaces.ONE)
    # Playable by number
    test_card_two = Card(CardColors.BLUE, CardFaces.THREE)
    # Playable by both
    test_card_three = Card(CardColors.YELLOW, CardFaces.THREE)
    # Playable by wild
    test_card_four = Card(CardColors.WILD, CardFaces.PLUS_FOUR)
    # Not playable
    test_card_five = Card(CardColors.RED, CardFaces.SEVEN)

    assert test_card_one.can_be_played(test_top_card)

    assert test_card_two.can_be_played(test_top_card)

    assert test_card_three.can_be_played(test_top_card)

    assert test_card_four.can_be_played(test_top_card)

    assert not test_card_five.can_be_played(test_top_card)
    

def test_can_be_jumped_in():
    """
    Tests that Card.can_be_jumped_in returns the correct value

    Raises:
        AssertionError: If any of the tests fail
    """

    test_top_card = Card(CardColors.YELLOW, CardFaces.THREE)

    # Playable by exact match
    test_card_one = Card(CardColors.YELLOW, CardFaces.THREE)
    # Not playable, color doesn't match
    test_card_two = Card(CardColors.BLUE, CardFaces.THREE)
    # Not playable, number doesn't match
    test_card_three = Card(CardColors.YELLOW, CardFaces.SEVEN)
    # Not playable, neither match
    test_card_four = Card(CardColors.BLUE, CardFaces.SEVEN)

    test_top_wild = Card(CardColors.BLUE, CardFaces.WILD)

    # Playable by matching wild face
    test_card_five = Card(CardColors.WILD, CardFaces.WILD)

    assert test_card_one.can_be_jumped_in(test_top_card)

    assert not test_card_two.can_be_jumped_in(test_top_card)

    assert not test_card_three.can_be_jumped_in(test_top_card)

    assert not test_card_four.can_be_jumped_in(test_top_card)

    assert test_card_five.can_be_jumped_in(test_top_wild)