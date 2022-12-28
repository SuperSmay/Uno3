from unogame.game import UnoGame, UnoRules, UnoStates, OutOfTurnError, OutOfCardsError, InvalidCardPlayedError, PlayerDoesNotHaveCardError
from unogame.player import Player
from unogame.card import Card, CardColors, CardFaces
from unogame.deck import DeckManager

def test_constructor():
     
    test_game = UnoGame()

    assert test_game.deck.__len__() == 107 # Not 108 because we drew a starting card
    assert test_game.players == []
    assert test_game.ruleset == UnoRules()
    assert test_game.state == UnoStates.PREGAME

def test_add_player():

    test_game = UnoGame()
    
    test_game.add_player(0)

    assert test_game.players == [Player(0)]

    assert test_game.players[0].hand.__len__() == test_game.ruleset.starting_hand_size

    test_game.add_player(1)
    test_game.add_player(2)

    assert test_game.players.__len__() == 3

    # This shouldn't work because we've already used this ID
    try:
        test_game.add_player(2)
        raise AssertionError("add_player should've thrown a ValueError")
    except ValueError as e:
        pass

def test_remove_player():

    test_game = UnoGame()
    
    test_game.add_player(0)
    test_game.add_player(1)
    test_game.add_player(2)

    test_game.remove_player(0)

    # This is what we should have now
    assert test_game.players == [Player(1), Player(2)]

    try:
        test_game.remove_player(0)
        raise AssertionError("remove_player should've thrown a ValueError")
    except ValueError as e:
        pass

    test_game.remove_player(1)
    test_game.remove_player(2)

    # Make sure all the cards ended up back in the deck
    assert len(test_game.deck) == 107 # Not 108 because a card was taken for starting card

def test_get_player():
    test_game = UnoGame()

    test_game.add_player(0)
    test_game.add_player(1)
    test_game.add_player(2)

    assert test_game.get_player(1) == Player(1)

def test_play_card_move():

    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    player_0.hand = [Card(CardColors.RED, CardFaces.SKIP), Card(CardColors.BLUE, CardFaces.EIGHT)]
    player_1.hand = [Card(CardColors.RED, CardFaces.FOUR), Card(CardColors.BLUE, CardFaces.NINE)]
    player_2.hand = [Card(CardColors.BLUE, CardFaces.EIGHT), Card(CardColors.BLUE, CardFaces.FIVE)]

    test_game.players.append(Player(0))
    test_game.players.append(Player(1))
    test_game.players.append(Player(2))
    
    test_game.deck.top_card = Card(CardColors.YELLOW, CardFaces.EIGHT)

    # First, have player 0 play a card they do have, but before the game started
    try:
        test_game.play_card_move(player_0, Card(CardColors.YELLOW, CardFaces.FIVE))
        raise AssertionError("play_card_move should have thrown an OutOfTurnError")
    except OutOfTurnError:
        # Nothing should have changed
        assert test_game.state == UnoStates.PREGAME
        assert test_game.turn_index == 0
        assert test_game.deck.top_card == Card(CardColors.YELLOW, CardFaces.EIGHT)

    test_game.start_game()

    # Now that the game has started, have player 0 play a card they don't have
    try:
        test_game.play_card_move(player_0, Card(CardColors.YELLOW, CardFaces.FIVE))
        raise AssertionError("play_card_move should have thrown a PlayerDoesNotHaveCardError")
    except PlayerDoesNotHaveCardError:
        # Nothing should have changed
        assert test_game.state == UnoStates.WAITING_FOR_PLAY
        assert test_game.turn_index == 0
        assert test_game.deck.top_card == Card(CardColors.YELLOW, CardFaces.EIGHT)

    # Then, have them play a card they do have and check that the state was updating accordingly
    test_game.play_card_move(player_0, Card(CardColors.BLUE, CardFaces.EIGHT))

    assert test_game.state == UnoStates.WAITING_FOR_PLAY
    assert test_game.turn_index == 1
    assert test_game.deck.top_card == Card(CardColors.BLUE, CardFaces.EIGHT)
    assert Card(CardColors.BLUE, CardFaces.EIGHT) not in player_0.hand

    # Then have player 1 play a card they have, but isn't a valid card
    try:
        test_game.play_card_move(player_1, Card(CardColors.RED, CardFaces.FOUR))
        raise AssertionError("play_card_move should have raised an InvalidCardPlayedError")
    except InvalidCardPlayedError:
        pass

    # Then have player 2 play out of turn (But a valid card)
    try:
        test_game.play_card_move(player_2, Card(CardColors.BLUE, CardFaces.FIVE))
        raise AssertionError("play_card_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    # Jump-in testing - This is a bit weird
    # First, player 2 tries a valid jump-in, but jump-ins are disabled (per default rules)
    try:
        test_game.play_card_move(player_2, Card(CardColors.BLUE, CardFaces.EIGHT))
        raise AssertionError("play_card_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    # Then modify the rules mid-game
    test_game.ruleset.jump_ins = True

    # Then have player 2 play a valid jump-in that they have
    test_game.play_card_move(player_2, Card(CardColors.BLUE, CardFaces.EIGHT))
    
    assert test_game.state == UnoStates.WAITING_FOR_PLAY
    assert test_game.turn_index == 0
    assert test_game.deck.top_card == Card(CardColors.BLUE, CardFaces.EIGHT)
    assert Card(CardColors.BLUE, CardFaces.EIGHT) not in player_2.hand

    # Now have player 2 try a jump-in again, but obviously they no longer have the card
    try:
        test_game.play_card_move(player_2, Card(CardColors.BLUE, CardFaces.EIGHT))
        raise AssertionError("play_card_move should have raised an PlayerDoesNotHaveCardError")
    except PlayerDoesNotHaveCardError:
        pass

