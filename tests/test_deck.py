from unogame.deck import *

def test_constructor():
    """
    Tests that the DeckManager constructor creates a correct deck, and creates the correct number of cards given a starting number of decks

    Raises:
        AssertionError: If any of the tests fail
    """

    test_deck = DeckManager()

    # Better have the right number of cards (108 cards total, 1 card designated top card)
    assert test_deck.draw_pile.__len__() == 107
    assert test_deck.discard_pile == []
    assert isinstance(test_deck.top_card, Card)

    test_deck = DeckManager(4)

    # Better have the right number of cards
    assert test_deck.draw_pile.__len__() == 108*4 - 1

    try:
        test_deck = DeckManager(0)
        raise AssertionError("DeckManager should've thrown a ValueError")
    except ValueError as e:
        pass
    

def test_len():
    """
    Tests that DeckManager.__len__() returns the correct value

    Raises:
        AssertionError: If the length returned is incorrect
    """

    test_deck = DeckManager()

    assert len(test_deck) == 107

    # Draw the card then discard it
    temp_card = test_deck.draw_card()
    test_deck.play_card(temp_card)

    assert len(test_deck) == 107
    

def test_draw_and_play_card():
    """
    Tests that DeckManager.draw_card and DeckManager.play_card work as described

    Raises:
        AssertionError: If the tests fail
    """

    test_deck = DeckManager()

    # Should work and not throw anything (108 cards in the deck, 1 card designated top card)
    for _ in range(107):
        test_deck.draw_card()

    # Should throw index error
    try:
        test_deck.draw_card()
        raise AssertionError("Draw card should've thrown an index error")
    except IndexError as e:
        pass

    # Manually play a couple cards (Play validity in the context of an Uno game is not checked!)
    test_deck.play_card(Card(CardColors.RED, CardFaces.SKIP))
    test_deck.play_card(Card(CardColors.BLUE, CardFaces.SEVEN))

    assert test_deck.top_card == Card(CardColors.BLUE, CardFaces.SEVEN)
    assert test_deck.discard_pile.__len__() == 2

    # Play a "ghost card" (Color chosen wild in this case.) It should not be added to the discard pile later
    test_deck.play_card(Card(CardColors.BLUE, CardFaces.WILD, return_to_discard=False))
    # Then play a normal card
    test_deck.play_card(Card(CardColors.RED, CardFaces.FOUR))

    # Make sure that ghost card is gone
    assert test_deck.top_card == Card(CardColors.RED, CardFaces.FOUR)
    assert Card(CardColors.BLUE, CardFaces.WILD) not in test_deck.discard_pile
    assert test_deck.discard_pile.__len__() == 3

    test_deck.draw_card()

    # Should've reshuffled discard pile into draw pile as draw pile was empty
    assert test_deck.discard_pile == []

    test_deck.draw_card()

    # Should have 1 card left in it after drawing 2 cards
    assert test_deck.draw_pile.__len__() == 1


def test_get_starting_card():
    """
    Tests that DeckManger.get_starting_card returns a valid starting card for an Uno game

    Raises:
        AssertionError: If any of the tests fail
    """

    test_deck = DeckManager()

    # Draw every card as a potential starting card until the only cards left are wild
    # Only 99 because the game starts with one drawn already, and there are 8 wilds/plus4s (out of a total 108)
    for _ in range(99):
        assert test_deck.draw_starting_card().color != CardColors.WILD

    # Make sure all the cards left are wild cards
    for card in test_deck.draw_pile:
        assert card.color == CardColors.WILD