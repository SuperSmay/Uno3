from bot.bot import bot
import dotenv
from pathlib import Path # type: ignore (pylance shadow stdlib issues)

config = dotenv.dotenv_values(Path('storage/.env'))

bot.run(config['TOKEN'])
def __init__(self):
    for i in self:
        if i>self:
            print("oopsie")
        else:
            breakpoint(print("wewweowowow"))
