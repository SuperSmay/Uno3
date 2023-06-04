from unogame.game import UnoGame, UnoRules, UnoStates, OutOfTurnError, OutOfCardsError, InvalidCardPlayedError, PlayerDoesNotHaveCardError, MustPlayCardError
from unogame.player import Player
from unogame.card import Card, CardColors, CardFaces
from unogame.deck import DeckManager

def test_constructor():
    """
    Tests that the constructor for UnoGame works as expected

    Raises:
        AssertionError: If any of the tests fail
    """
     
    test_game = UnoGame()

    assert test_game.deck.__len__() == 107 # Not 108 because we drew a starting card
    assert test_game.players == []
    assert test_game.ruleset == UnoRules()
    assert test_game.state == UnoStates.PREGAME


def test_create_player():
    """
    Tests that UnoGame.create_player adds a player correctly

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()
    
    # Should add a new player with an ID of 0
    test_game.create_player(0)

    assert test_game.players == [Player(0)]

    assert test_game.players[0].hand.__len__() == test_game.ruleset.starting_hand_size

    test_game.create_player(1)
    test_game.create_player(2)

    assert test_game.players.__len__() == 3

    # This shouldn't work because we've already used this ID
    try:
        test_game.create_player(2)
        raise AssertionError("add_player should've thrown a ValueError")
    except ValueError as e:
        pass


def test_remove_player():
    """
    Tests that UnoGame.remove_player works as expected

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()
    
    test_game.create_player(0)
    test_game.create_player(1)
    test_game.create_player(2)

    test_game.remove_player(0)

    # This is what we should have now
    assert test_game.players == [Player(1), Player(2)]

    # This shouldn't work because there is no player with ID 0
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
    """
    Tests that UnoGame.get_player returns the correct player

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()

    test_game.create_player(0)
    test_game.create_player(1)
    test_game.create_player(2)

    # Manually get the player with ID 1 from the list of players (Thanks https://stackoverflow.com/a/2364277)
    player = next(player for player in test_game.players if player.player_id == 1)
    assert test_game.get_player(1) == player


def test_is_players_turn():
    """
    Tests that UnoGame.is_players_turn returns the correct value

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()

    test_game.create_player(0)
    test_game.create_player(1)
    test_game.create_player(2)

    # Manually get the player with ID 1 from the list of players (Thanks https://stackoverflow.com/a/2364277)
    player0 = next(player for player in test_game.players if player.player_id == 0)
    player1 = next(player for player in test_game.players if player.player_id == 1)
    assert test_game.is_players_turn(player0)
    assert not test_game.is_players_turn(player1)


def test_next_turn_index():
    """
    Tests that UnoGame._next_turn_index returns the correct value
    
    Raises:
        AssertionError: If any of the tests fail
    
    """

    test_game = UnoGame()

    test_game.create_player(0)
    test_game.create_player(1)
    test_game.create_player(2)

    test_game.turn_index = 0

    # Should be a simple increment
    assert test_game._next_turn_index(1) == 1
    # More complex now
    assert test_game._next_turn_index(2) == 2
    assert test_game._next_turn_index(3) == 0


    test_game.reversed = True

    # Now test it backwards with various sizes
    assert test_game._next_turn_index(1) == 2
    assert test_game._next_turn_index(2) == 1
    assert test_game._next_turn_index(3) == 0

    # Now 2 players
    test_game.remove_player(2)
    test_game.reversed = False

    assert test_game._next_turn_index(1) == 1
    assert test_game._next_turn_index(2) == 0
    assert test_game._next_turn_index(3) == 1

    # Now 1 player (not that is really going to happen in a game but still)
    test_game.remove_player(1)

    assert test_game._next_turn_index(1) == 0
    assert test_game._next_turn_index(2) == 0



def test_basic_play_card_move():
    """
    Tests that UnoGame.play_card_move works in basic cases, and that the game state is updating correctly.
    Also tests when players are allowed to play cards (again, not including jump-ins).
    Does not cover jump-ins, special cards like reverses, skips, plus cards, and wilds.


    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    player_0.hand = [Card(CardColors.RED, CardFaces.SKIP), Card(CardColors.BLUE, CardFaces.EIGHT)]
    player_1.hand = [Card(CardColors.RED, CardFaces.FOUR), Card(CardColors.BLUE, CardFaces.NINE)]
    player_2.hand = [Card(CardColors.BLUE, CardFaces.EIGHT), Card(CardColors.BLUE, CardFaces.FIVE)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
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

    # This concludes the tests for the simple card playing stuff

def test_jump_ins():
    """
    Tests that basic jump-ins work correctly, and that game state is updated accordingly.
    Also tests when players are allowed to jump-in
    Does not include special cards like reverses, plus cards, etc.

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    player_0.hand = [Card(CardColors.RED, CardFaces.SKIP), Card(CardColors.BLUE, CardFaces.EIGHT)]
    player_1.hand = [Card(CardColors.RED, CardFaces.FOUR), Card(CardColors.BLUE, CardFaces.NINE)]
    player_2.hand = [Card(CardColors.BLUE, CardFaces.EIGHT), Card(CardColors.BLUE, CardFaces.FIVE)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
    test_game.deck.top_card = Card(CardColors.BLUE, CardFaces.EIGHT)

    # Of course nothing can happen before the game starts
    try:
        test_game.play_card_move(player_2, Card(CardColors.BLUE, CardFaces.EIGHT))
        raise AssertionError("play_card_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    test_game.start_game()

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

    # This concludes the testing for simple jump-ins

def test_reverse_skip_cards():
    """
    Tests that reverse and skip cards work as expected, including jump-ins and 1v1s.
    Does not test the basic mechanics of playing a card, as those are covered in test_basic_play_card_move.

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    # All of the cards are green to make my life easier
    # Player 0 has lots of cards to stop them from winning during this test
    player_0.hand = [Card(CardColors.GREEN, CardFaces.SKIP), Card(CardColors.GREEN, CardFaces.REVERSE), Card(CardColors.GREEN, CardFaces.EIGHT), Card(CardColors.GREEN, CardFaces.EIGHT)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.SKIP), Card(CardColors.GREEN, CardFaces.NINE)]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.SKIP), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.NINE)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    test_game.ruleset.jump_ins = True

    test_game.start_game()

    # We are not going to test the various edge cases for when cards can be played here,
    # or if the cards are removed properly.
    # Those are covered in test_basic_play_card_move and test_jump_ins,
    # this test is for game state changes due to reverse and skip cards.

    # Player 0 skips player 1, it is now player 2's turn
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.SKIP))

    assert test_game.turn_index == 2

    # Player 1 jumps in and skips player 2, it is now player 0's turn
    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.SKIP))

    assert test_game.turn_index == 0

    # Player 0 reverses direction, it is now player 2's turn
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.REVERSE))

    assert test_game.turn_index == 2
    assert test_game.reversed

    # Player 2 skips player 1, its now player 0's turn
    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.SKIP))

    assert test_game.turn_index == 0
    assert test_game.reversed

    # Player 0 plays a normal card, play moves back to player 2
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.EIGHT))

    assert test_game.turn_index == 2
    assert test_game.reversed

    # Player 2 plays a normal card, play moves back to player 1
    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.SEVEN))

    assert test_game.turn_index == 1
    assert test_game.reversed

    # We also need to test 1v1 reverses acting as skips.
    # Reset the game completely
    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)

    # All of the cards are green to make my life easier
    # Player 0 has lots of cards to stop them from winning during this test
    player_0.hand = [Card(CardColors.GREEN, CardFaces.SKIP), Card(CardColors.GREEN, CardFaces.REVERSE), Card(CardColors.GREEN, CardFaces.EIGHT)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.SKIP), Card(CardColors.GREEN, CardFaces.NINE)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    test_game.ruleset.jump_ins = True

    test_game.start_game()

    # Player 0 plays a reverse, which should skip player 1 and make it player 0's turn again
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.REVERSE))

    assert test_game.turn_index == 0
    assert test_game.reversed

    # Player 0 plays a skip, which should skip player 1 and make it player 0's turn again
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.SKIP))

    assert test_game.turn_index == 0
    assert test_game.reversed

    # Player 1 jumps in with a skip of their own, making it their turn again
    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.SKIP))

    assert test_game.turn_index == 1
    assert test_game.reversed

def test_draw_card_move():
    """
    Test that a draw card move works as expected, and that game state is updated accordingly.
    Also tests when players are allowed to draw a card, and how many cards they draw.

    Raises:
        AssertionError: If a test fails
    """

    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)

    player_0.hand = [Card(CardColors.RED, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.EIGHT)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    test_game.start_game()

    # We're going to test in single draw mode for most of this to make it easier
    test_game.ruleset.draw_until_can_play = False

    # Start with forceplay on
    test_game.ruleset.force_play = True

    # Because forceplay is on and they have a valid move, player 0 should not be able to choose to draw a card
    try:
        test_game.draw_card_move(player_0)
        raise AssertionError("draw_card_move should have raised a MustPlayCardError")
    except MustPlayCardError:
        pass

    # Then disable forceplay and check that the player draws a card now
    test_game.ruleset.force_play = False
    test_game.draw_card_move(player_0)

    assert player_0.hand.__len__() == 3

    # Their turn should now be over
    assert test_game.turn_index == 1

    # Player 1 plays a plus two, so player 0 must now accept that draw
    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    test_game.draw_card_move(player_0)

    assert player_0.hand.__len__() == 5

    # Now reset the game and test multi-draw
    # This test is not great because it could occasionally pass due to RNG but its good enough
    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)

    # All of the cards are green to make my life easier
    # Player 0 has lots of cards to stop them from winning during this test
    player_0.hand = [Card(CardColors.RED, CardFaces.ONE), Card(CardColors.BLUE, CardFaces.NINE)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    test_game.start_game()

    # Draw 'til you die
    test_game.ruleset.draw_until_can_play = True

    # Start with forceplay on
    test_game.ruleset.force_play = True

    # Player 0 has no valid moves, so they draw
    test_game.draw_card_move(player_0)

    # If they only drew one card, that could have been a random single card draw that succeeded, so we try again
    while player_0.hand.__len__() == 3:
        # Remove the last card the player drew
        player_0.hand.pop()
        # Reset the turn
        test_game.turn_index = 0
        test_game.state = UnoStates.WAITING_FOR_PLAY
        # Try again
        test_game.draw_card_move(player_0)

        if len(test_game.deck.draw_pile) == 0:
            # Oops we ran out of cards.
            # Either the test failed because draw_card_move only drew one card even with draw_until_can_play set to True,
            # or because it got incredibly unlucky (lucky?) and drew all the valid cards one after the other until it ran out of valid cards.

            # If the player has three cards and the deck is out of cards, then it definitely just kept drawing one, 
            # because it should have stopped drawing when a valid card was found instead of just drawing one at a time,
            # and would have drawn all of the rest of the deck (more than three cards) if it just got unlucky
            if len(player_0.hand) == 3:
                raise AssertionError("draw_card_move only drew one card until the deck ran out of cards")
            
            # At this point I think its fair to pass the test. All valid cards were drawn one at a time, and after the last valid card was gone,
            # it drew the rest of the deck.
            player_0.add_card_to_hand(Card(CardColors.GREEN, CardFaces.EIGHT))
            break


    # They should have drawn a card that they can play
    assert player_0.has_card_to_play(test_game.deck.top_card)

    # They shouldn't be able to draw twice
    try:
        test_game.draw_card_move(player_0)
        raise AssertionError("draw_card_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    assert test_game.state == UnoStates.WAITING_FOR_DRAW_RESPONSE

    # The last card they drew should be the one they can play
    test_game.play_card_move(player_0, player_0.hand[-1])

    # Reset the top card to what it was before
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    # They should only have one card that could be played on that, and they just played it
    assert not player_0.has_card_to_play(test_game.deck.top_card)


def test_play_card_move_no_stacking():
    """
    Tests that plus 2 cards work as expected when stacking is off.
    Also tests that players draw the right number of cards.
    Does not test plus 4s.
    Does not test jump-ins.
    Does not test the basic mechanics of playing a card, as those are covered in test_basic_play_card_move.

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    # All of the cards are green to make my life easier
    player_0.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR),]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    test_game.start_game()

    # Test the simplest case first
    test_game.ruleset.stacking = False
    test_game.ruleset.jump_ins = False

    # Player 1 now has to draw two cards
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    assert test_game.current_stack == 2

    try:
        # This shouldn't work because stacking is off
        test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.PLUS_TWO))
        raise AssertionError("play_card_move should've raised an InvalidCardPlayedError")
    except InvalidCardPlayedError:
        pass

    try:
        # This shouldn't work because player 2 is not the one who needs to accept the cards
        test_game.draw_card_move(player_2)
        raise AssertionError("draw_card_move should've raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    # This one should work
    test_game.draw_card_move(player_1)

    assert test_game.current_stack == 0
    assert len(player_1.hand) == 5


def test_plus_response_basic_stacking():
    """
    Tests that plus cards work with stacking correctly.
    Also tests that choose_color_move works correctly.

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    # All of the cards are green to make my life easier
    player_0.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR),]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    test_game.start_game()

    # Test basic stacking (plus fours -> plus fours and plus twos -> plus twos)
    test_game.ruleset.stacking = True

    test_game.ruleset.stack_all_plus_twos_on_plus_fours = False
    test_game.ruleset.stack_color_matching_plus_twos_on_plus_fours = False
    test_game.ruleset.stack_plus_fours_on_plus_twos = False
    test_game.ruleset.jump_ins = False

    # Player 0 starts by playing a plus two
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    assert test_game.current_stack == 2

    # Player 2 then tries (and fails because its not their turn) to stack on it
    try:
        test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.PLUS_TWO))
        raise AssertionError("play_card_move should've raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    # Player 1 then adds to the stack
    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    assert test_game.current_stack == 4

    # Player 2 then adds as well
    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    assert test_game.current_stack == 6

    # Player 0 tries to stack the plus four, and fails because thats not allowed right now
    try:
        test_game.play_card_move(player_0, Card(CardColors.WILD, CardFaces.PLUS_FOUR))
        raise AssertionError("play_card_move should have raised an InvalidCardPlayedError")
    except InvalidCardPlayedError:
        pass

    assert test_game.current_stack == 6

    # Player 0 accepts the stack
    test_game.draw_card_move(player_0)

    assert player_0.hand.__len__() == 8
    assert test_game.current_stack == 0

    # Player 1 starts another stack by playing a plus four
    test_game.play_card_move(player_1, Card(CardColors.WILD, CardFaces.PLUS_FOUR))

    assert test_game.current_stack == 0

    # Player 2 tries to stack, but fails because player 1 must choose a color
    try:
        test_game.play_card_move(player_2, Card(CardColors.WILD, CardFaces.PLUS_FOUR))
        raise AssertionError("play_card_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    # Player 2 then tries to choose a color, but fails because player 1 must choose a color
    try:
        test_game.choose_color_move(player_2, CardColors.BLUE)
        raise AssertionError("choose_color_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    # Player 1 then tries to choose a color, but fails because CardColors.WILD is not a valid color choice
    try:
        test_game.choose_color_move(player_1, CardColors.WILD)
        raise AssertionError("choose_color_move should have raised an OutOfTurnError")
    except InvalidCardPlayedError:
        pass

    # Player 1 does it right
    test_game.choose_color_move(player_1, CardColors.GREEN)

    # Player 2 then tries to choose a color, but fails because the game is not waiting for them to choose a color
    try:
        test_game.choose_color_move(player_2, CardColors.BLUE)
        raise AssertionError("choose_color_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    assert test_game.current_stack == 4

    # Now player 2 can stack
    test_game.play_card_move(player_2, Card(CardColors.WILD, CardFaces.PLUS_FOUR))
    test_game.choose_color_move(player_2, CardColors.GREEN)

    assert test_game.current_stack == 8

    # Player 0 tries to stack the plus two, and fails because thats not allowed right now
    try:
        test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.PLUS_TWO))
        raise AssertionError("play_card_move should have raised an InvalidCardPlayedError")
    except InvalidCardPlayedError:
        pass

    # Player 0 then adds another plus four
    test_game.play_card_move(player_0, Card(CardColors.WILD, CardFaces.PLUS_FOUR))
    test_game.choose_color_move(player_0, CardColors.GREEN)

    # Player 1 accepts the stack
    test_game.draw_card_move(player_1)

    assert player_1.hand.__len__() == 13


def test_asymmetric_plus_stacks():
    """
    Tests that plus stacks with different types of plus cards work correctly.
    Does not test that basic stacking works, or the edge cases of basic stacking.
    Does not test choose_color_move.

    Raises:
        AssertionError: If any of the tests fail
    """
    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    # All of the cards are green to make my life easier
    player_0.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]
    player_2.hand = [Card(CardColors.RED, CardFaces.PLUS_TWO), Card(CardColors.RED, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    test_game.start_game()

    # Test asymmetric stacking (plus fours -> plus twos and plus twos -> plus fours)
    test_game.ruleset.stacking = True

    test_game.ruleset.stack_all_plus_twos_on_plus_fours = True
    test_game.ruleset.stack_color_matching_plus_twos_on_plus_fours = False
    test_game.ruleset.stack_plus_fours_on_plus_twos = True
    test_game.ruleset.jump_ins = False

    # Player 0 starts by playing a plus two
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    assert test_game.current_stack == 2

    # Player 1 then adds to the stack with a plus 4
    test_game.play_card_move(player_1, Card(CardColors.WILD, CardFaces.PLUS_FOUR))

    assert test_game.current_stack == 2

    # Player 1 chooses a color
    test_game.choose_color_move(player_1, CardColors.GREEN)

    assert test_game.current_stack == 6

    # Player 2 then adds as well (All colors of plus two should work per current rules)
    test_game.play_card_move(player_2, Card(CardColors.RED, CardFaces.PLUS_TWO))

    assert test_game.current_stack == 8

    # Player 0 accepts the stack
    test_game.draw_card_move(player_0)

    assert player_0.hand.__len__() == 10
    assert test_game.current_stack == 0

    test_game.ruleset.stack_all_plus_twos_on_plus_fours = False
    test_game.ruleset.stack_color_matching_plus_twos_on_plus_fours = True

    # Player 1 starts another stack by playing a plus four
    test_game.play_card_move(player_1, Card(CardColors.WILD, CardFaces.PLUS_FOUR))

    assert test_game.current_stack == 0

    # Then picks a color
    test_game.choose_color_move(player_1, CardColors.GREEN)

    assert test_game.current_stack == 4

    # Now player 2 tries to stack the wrong color plus two
    try:
        test_game.play_card_move(player_2, Card(CardColors.RED, CardFaces.PLUS_TWO))
        raise AssertionError("play_card_move should have raised an InvalidCardPlayedError")
    except InvalidCardPlayedError:
        pass

    assert test_game.current_stack == 4

    # Then does it right
    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    assert test_game.current_stack == 6

    # Player 0 accepts the stack
    test_game.draw_card_move(player_0)

    assert player_0.hand.__len__() == 16


def test_jump_in_stacks():
    """
    Tests that stacks work correctly with jump-ins.
    Does not test basic stack mechanics.

    Raises:
        AssertionError: If any of the tests fail
    """
    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    # All of the cards are green to make my life easier
    player_0.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR),]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    test_game.start_game()

    # Test jump-in stacking (plus fours -> plus fours and plus twos -> plus twos)
    test_game.ruleset.stacking = True
    test_game.ruleset.jump_ins = True

    test_game.ruleset.stack_all_plus_twos_on_plus_fours = False
    test_game.ruleset.stack_color_matching_plus_twos_on_plus_fours = False
    test_game.ruleset.stack_plus_fours_on_plus_twos = False

    # First test the rule that the stack clears after jump-ins
    test_game.ruleset.jump_ins_stack = False

    # Player 0 starts by playing a plus two
    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    assert test_game.current_stack == 2

    # Player 2 then jumps in
    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.PLUS_TWO))

    # Stack should have cleared
    assert test_game.current_stack == 2

    # Player 0 then accepts stack
    test_game.draw_card_move(player_0)

    assert test_game.current_stack == 0

    # Now jump-ins preserve the stack
    test_game.ruleset.jump_ins_stack = True

    # Player 1 starts another stack by playing a plus four
    test_game.play_card_move(player_1, Card(CardColors.WILD, CardFaces.PLUS_FOUR))

    assert test_game.current_stack == 0

    # Player 0 tries to jump-in, but fails because player 1 must choose a color
    try:
        test_game.play_card_move(player_0, Card(CardColors.WILD, CardFaces.PLUS_FOUR))
        raise AssertionError("play_card_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    test_game.choose_color_move(player_1, CardColors.GREEN)

    assert test_game.current_stack == 4

    # Now player 0 can jump-in stack the plus 4
    test_game.play_card_move(player_0, Card(CardColors.WILD, CardFaces.PLUS_FOUR))
    test_game.choose_color_move(player_0, CardColors.GREEN)

    assert test_game.current_stack == 8

    # Player 1 accepts the stack
    test_game.draw_card_move(player_1)

    assert len(player_1.hand) == 10

def test_pass_move():
    """
    Tests that passing can only happen in the allowed cases.

    Raises:
        AssertionError: If any of the tests fail
    """

    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)

    player_0.hand = [Card(CardColors.RED, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.EIGHT)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    
    test_game.deck.top_card = Card(CardColors.YELLOW, CardFaces.SIX)

    test_game.start_game()

    test_game.ruleset.draw_until_can_play = True
    test_game.ruleset.force_play = True

    # You cannot pass before drawing cards
    try:
        test_game.pass_turn_move(player_0)
        raise AssertionError("pass_turn_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass 

    test_game.draw_card_move(player_0)

    # Because forceplay and draw_until_can_play are on, it doesn't matter if they can play or not after drawing. Player 0 should not be able to pass
    try:
        test_game.pass_turn_move(player_0)
        raise AssertionError("pass_turn_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass 

    # Then disable forceplay and check that the player can pass now
    test_game.ruleset.force_play = False

    test_game.pass_turn_move(player_0)

    assert test_game.turn_index == 1


def test_zero_rotate():
    """
    Tests that the zero rotate rule works correctly.
    Also tests the various sub rules related to zero rotate.

    Raises:
        AssertionError: If any of the tests fail
    """
    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    player_0.hand = [Card(CardColors.RED, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.YELLOW, CardFaces.FIVE)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
    test_game.deck.top_card = Card(CardColors.RED, CardFaces.SIX)

    test_game.start_game()

    test_game.ruleset.zero_rotate_hands = True
    test_game.ruleset.force_zero_rotate = True

    # Can't make a rotate happen yet
    try:
        test_game.zero_rotate_move(player_0, True)
        raise AssertionError("zero_rotate_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass 

    test_game.play_card_move(player_0, Card(CardColors.RED, CardFaces.ZERO))

    assert test_game.state == UnoStates.WAITING_FOR_CHOOSE_TO_ROTATE

    # You cannot deny the rotate if force_zero_rotate is on
    try:
        test_game.zero_rotate_move(player_0, False)
        raise AssertionError("zero_rotate_move should have raised an ValueError")
    except ValueError:
        pass 

    # Wrong player
    try:
        test_game.zero_rotate_move(player_1, True)
        raise AssertionError("zero_rotate_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass 

    # Do it right
    test_game.zero_rotate_move(player_0, True)

    # Make sure it worked
    assert player_0.hand == [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]

    # Now make it optional 
    test_game.ruleset.force_zero_rotate = False

    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.ZERO))
    # This should be optional now
    test_game.zero_rotate_move(player_1, False)

    # Make sure nothing changed
    assert player_0.hand == [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]

    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.REVERSE))

    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.ZERO))

    test_game.zero_rotate_move(player_1, True)

    # Make sure reverse worked
    assert player_0.hand == [Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    # Move index for the sake of this test being easier to write :D
    test_game.turn_index = 2
    test_game.reversed = False

    # Make sure nothing happens if zero rule is off
    test_game.ruleset.zero_rotate_hands = False
    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.ZERO))

    assert test_game.state == UnoStates.WAITING_FOR_PLAY

    # Turn that back on
    test_game.ruleset.zero_rotate_hands = True

    # Reset hands to test jump-ins
    player_0.hand = [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO)]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO)]

    # First, the jump-ins can cancel zeros
    test_game.ruleset.jump_in_during_zero = True
    test_game.ruleset.jump_ins = True

    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.ZERO))
    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.ZERO))

    assert test_game.state == UnoStates.WAITING_FOR_CHOOSE_TO_ROTATE
    assert test_game.turn_index == 1

    # Now they can't
    test_game.ruleset.jump_in_during_zero = False
    try:
        test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.ZERO))
        raise AssertionError("play_card_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass 


def test_seven_swap():
    """
    Tests that the seven swap rule works correctly.
    Also tests the various sub rules related to seven swap.

    Raises:
        AssertionError: If any of the tests fail
    """
    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    player_0.hand = [Card(CardColors.RED, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.YELLOW, CardFaces.FIVE)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    test_game.players.append(player_0)
    test_game.players.append(player_1)
    test_game.players.append(player_2)
    
    test_game.deck.top_card = Card(CardColors.RED, CardFaces.SIX)

    test_game.start_game()

    test_game.ruleset.seven_swap_hands = True
    test_game.ruleset.force_seven_swap = True

    # Can't make a swap happen yet
    try:
        test_game.seven_swap_move(player_0, 1)
        raise AssertionError("seven_swap_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass 

    test_game.play_card_move(player_0, Card(CardColors.RED, CardFaces.SEVEN))

    assert test_game.state == UnoStates.WAITING_FOR_PICK_PLAYER_TO_SWAP

    # You cannot deny the swap (swap with yourself) if force_seven_swap is on
    try:
        test_game.seven_swap_move(player_0, 0)
        raise AssertionError("seven_swap_move should have raised an ValueError")
    except ValueError:
        pass 

    # Wrong player
    try:
        test_game.seven_swap_move(player_1, 2)
        raise AssertionError("seven_swap_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass 

    # Invalid index
    try:
        test_game.seven_swap_move(player_0, 9)
        raise AssertionError("seven_swap_move should have raised an IndexError")
    except IndexError:
        pass 

    # Do it right
    test_game.seven_swap_move(player_0, 1)

    # Make sure it worked
    assert player_0.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    # Now make it optional 
    test_game.ruleset.force_seven_swap = False

    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.SEVEN))
    # This should be optional now
    test_game.seven_swap_move(player_1, 1)

    # Make sure nothing changed
    assert player_0.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    # Make sure nothing happens if seven rule is off
    test_game.ruleset.seven_swap_hands = False
    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.SEVEN))

    assert test_game.state == UnoStates.WAITING_FOR_PLAY

    # Turn that back on
    test_game.ruleset.seven_swap_hands = True

    # Reset hands to test jump-ins
    player_0.hand = [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN)]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN)]

    # First, the jump-ins can cancel sevens
    test_game.ruleset.jump_in_during_seven = True
    test_game.ruleset.jump_ins = True

    test_game.play_card_move(player_0, Card(CardColors.GREEN, CardFaces.SEVEN))
    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.SEVEN))

    assert test_game.state == UnoStates.WAITING_FOR_PICK_PLAYER_TO_SWAP
    assert test_game.turn_index == 1

    # Now they can't
    test_game.ruleset.jump_in_during_seven = False
    try:
        test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.SEVEN))
        raise AssertionError("seven_swap_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass 