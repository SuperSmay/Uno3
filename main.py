from bot.bot import bot
import dotenv
from pathlib import Path # type: ignore (pylance shadow stdlib issues)

config = dotenv.dotenv_values(Path('storage/.env'))

bot.run(config['TOKEN'])
