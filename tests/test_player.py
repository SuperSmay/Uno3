from unogame.player import *
from unogame.card import CardColors, CardFaces

def test_constructor():
    test_player = Player(69)

    assert test_player.player_id == 69

    assert test_player.hand == []

def test_add_to_hand():
    test_player = Player(0)

    test_player.add_card_to_hand(Card(CardColors.BLUE, CardFaces.EIGHT))

    assert test_player.hand == [Card(CardColors.BLUE, CardFaces.EIGHT)]

    assert not test_player.play_card(Card(CardColors.RED, CardFaces.ONE))

    assert test_player.play_card(Card(CardColors.BLUE, CardFaces.EIGHT))

def test_play_card():
    test_player = Player(0)

    test_player.hand = [Card(CardColors.BLUE, CardFaces.EIGHT)]

    assert not test_player.play_card(Card(CardColors.RED, CardFaces.ONE))

    assert test_player.play_card(Card(CardColors.BLUE, CardFaces.EIGHT))

def test_has_card_to_play():
    test_player = Player(0)

    test_player.hand = [Card(CardColors.BLUE, CardFaces.EIGHT), Card(CardColors.RED, CardFaces.ONE)]

    test_top_card = Card(CardColors.YELLOW, CardFaces.ONE)

    assert test_player.has_card_to_play(test_top_card)

    test_top_card = Card(CardColors.YELLOW, CardFaces.TWO)

    assert not test_player.has_card_to_play(test_top_card)