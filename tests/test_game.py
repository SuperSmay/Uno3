from unogame.game import UnoGame, UnoRules, UnoStates, OutOfTurnError, OutOfCardsError, InvalidCardPlayedError, PlayerDoesNotHaveCardError, MustPlayCardError
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

def test_basic_play_card_move():

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

    # Now reset the game and test multi-draw
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

    # They should have drawn a card that they can play
    assert player_0.has_card_to_play(test_game.deck.top_card)

    # They shouldn't be able to draw twice
    try:
        test_game.draw_card_move(player_0)
        raise AssertionError("draw_card_move should have raised an OutOfTurnError")
    except OutOfTurnError:
        pass

    # The last card they drew should be the one they can play
    test_game.play_card_move(player_0, player_0.hand[-1])

    # Reset the top card to what it was before
    test_game.deck.top_card = Card(CardColors.GREEN, CardFaces.EIGHT)

    # They should only have one card that could be played on that
    assert not player_0.has_card_to_play(test_game.deck.top_card)

def test_play_card_move_no_stacking():

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

    test_game.choose_color_move(player_1, CardColors.GREEN)

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

    # Player 1 then adds to the stack
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

    # First test that the stack clears after jump-ins
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

    # Now player 0 can jump-in stack
    test_game.play_card_move(player_0, Card(CardColors.WILD, CardFaces.PLUS_FOUR))
    test_game.choose_color_move(player_0, CardColors.GREEN)

    assert test_game.current_stack == 8

    # Player 1 accepts the stack
    test_game.draw_card_move(player_1)

    assert len(player_1.hand) == 10

def test_pass_move():

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
    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    player_0.hand = [Card(CardColors.RED, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.YELLOW, CardFaces.FIVE)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

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
    assert player_0.hand == [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]

    # Now make it optional 
    test_game.ruleset.force_zero_rotate = False

    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.ZERO))
    # This should be optional now
    test_game.zero_rotate_move(player_1, False)

    # Make sure nothing changed
    assert player_0.hand == [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.ZERO), Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]

    test_game.play_card_move(player_2, Card(CardColors.GREEN, CardFaces.REVERSE))

    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.ZERO))

    test_game.zero_rotate_move(player_1, True)

    # Make sure reverse worked
    assert player_0.hand == [Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

def test_seven_swap():
    test_game = UnoGame()
    
    # Manually add players to set up a specific game state
    player_0 = Player(0)
    player_1 = Player(1)
    player_2 = Player(2)

    player_0.hand = [Card(CardColors.RED, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.YELLOW, CardFaces.FIVE)]
    player_1.hand = [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]
    player_2.hand = [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

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

    # You cannot deny the swap if force_seven_swap is on
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
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    # Now make it optional 
    test_game.ruleset.force_seven_swap = False

    test_game.play_card_move(player_1, Card(CardColors.GREEN, CardFaces.SEVEN))
    # This should be optional now
    test_game.seven_swap_move(player_1, 1)

    # Make sure nothing changed
    assert player_0.hand == [Card(CardColors.GREEN, CardFaces.ONE), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.REVERSE)]
    assert player_1.hand == [Card(CardColors.GREEN, CardFaces.SEVEN), Card(CardColors.YELLOW, CardFaces.FIVE)]
    assert player_2.hand == [Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.GREEN, CardFaces.PLUS_TWO), Card(CardColors.WILD, CardFaces.PLUS_FOUR)]

    #TODO jump in cancels swap rules