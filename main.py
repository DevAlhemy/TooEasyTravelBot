from database.database import create_table
from settings.bot_system import bot


if __name__ == '__main__':
    create_table()
    bot.infinity_polling()
