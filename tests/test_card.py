from unogame.card import *

def test_get_emoji_mention():
    test_card: Card = Card(CardColors.BLUE, CardFaces.PLUS_TWO)
    assert test_card.get_emoji_mention() == "<:plus2_blue:736430793815097416>"

def test_get_image_url():
    test_card: Card = Card(CardColors.GREEN, CardFaces.FIVE)
    assert test_card.get_image_url() == "https://cdn.discordapp.com/attachments/742986384113008712/742986667438112869/Background_47.png"