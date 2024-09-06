from .constants import (
    KEY_HELP,
    WELCOME,
    INSTRUCTION,
    KEY_LOWPRICE,
    KEY_BESTDEAL,
    KEY_RATING,
    KEY_HISTORY,
    HELP,
    CITY,
)
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.lowprice import city_name_low
from utils.bestdeal import city_name_dist
from utils.rating import city_name_rate
from utils.history import show_history
from .loader import bot


@bot.message_handler(commands=["start"])
def start_command(message):
    key = InlineKeyboardMarkup()
    key_help = InlineKeyboardButton(KEY_HELP, callback_data="help")
    key.add(key_help)
    bot.send_message(
        message.chat.id, WELCOME.format(message.from_user.first_name), reply_markup=key
    )
    bot.send_message(message.chat.id, INSTRUCTION)


@bot.message_handler(commands=["help"])
def help_command(message):
    key = InlineKeyboardMarkup()
    key_lowprice = InlineKeyboardButton(KEY_LOWPRICE, callback_data="lowprice")
    key_bestdeal = InlineKeyboardButton(KEY_BESTDEAL, callback_data="bestdeal")
    key_rating = InlineKeyboardButton(KEY_RATING, callback_data="rating")
    key_history = InlineKeyboardButton(KEY_HISTORY, callback_data="history")
    key.add(key_lowprice, key_bestdeal, key_rating, key_history)
    bot.send_message(message.chat.id, HELP, reply_markup=key)


@bot.message_handler(commands=["lowprice"])
def low_command(message):
    bot.send_message(message.chat.id, CITY)
    bot.register_next_step_handler(message, city_name_low)


@bot.message_handler(commands=["bestdeal"])
def dist_command(message):
    bot.send_message(message.chat.id, CITY)
    bot.register_next_step_handler(message, city_name_dist)


@bot.message_handler(commands=["rating"])
def rate_command(message):
    bot.send_message(message.chat.id, CITY)
    bot.register_next_step_handler(message, city_name_rate)


@bot.message_handler(commands=["history"])
def history_command(message):
    show_history(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    bot.answer_callback_query(call.id)
    if call.data == "help":
        help_command(call.message)
    elif call.data == "lowprice":
        low_command(call.message)
    elif call.data == "bestdeal":
        dist_command(call.message)
    elif call.data == "rating":
        rate_command(call.message)
    elif call.data == "history":
        history_command(call.message)
