from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from settings.constants import (
    CORRECTION,
    ARRIVAL_DATE,
    COUNT_HOTEL,
    NOT_FIND,
    KEY_URL,
    KEY_PHOTO,
    HOTEL,
    REPEAT_FIND,
    ERROR_CITY,
    ERROR_UN,
    ERROR_VALUE,
    ERROR_HOTEL,
    ERROR_PHOTO,
)
from settings.loader import (
    bot,
    QUERY_LOCATION,
    QUERY_HOTEL_RATE,
    URL_HOTEL,
    HEADERS,
    QUERY_PHOTO,
    URL_PHOTO,
    URL_LOCATION,
)
import requests
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta, datetime
from handlers.history import save_query


user_data = {}


def search_city_rate(message):
    QUERY_LOCATION["text"] = str(message.text)

    try:
        response = requests.get(URL_LOCATION, headers=HEADERS, params=QUERY_LOCATION)
        response.raise_for_status()
        location = response.json()

        city_list = []
        dest_id = []
        for loc in location:
            city_list.append(loc["name"])
            dest_id.append(loc["dest_id"])

        town_loc = dict(zip(city_list, dest_id))

        chat_id = message.chat.id
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]["town_loc"] = town_loc

        key = InlineKeyboardMarkup(row_width=1)
        for loc in town_loc:
            key_city = InlineKeyboardButton(
                loc, callback_data="city_rate" + town_loc[loc]
            )
            key.add(key_city)

        bot.send_message(message.chat.id, CORRECTION, reply_markup=key)
    except requests.RequestException:
        bot.send_message(message.chat.id, ERROR_CITY)
    except Exception:
        bot.send_message(message.chat.id, ERROR_UN)


def city_name_rate(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]["city_input"] = message.text
    search_city_rate(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("city_rate"))
def callback_arrival_rate(call):
    chat_id = call.message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]["dest_id"] = str(call.data[len("city_rate") :])
    town_loc = user_data[chat_id].get("town_loc", {})
    user_data[chat_id]["city_name"] = next(
        key for key, value in town_loc.items() if value == user_data[chat_id]["dest_id"]
    )
    calendar, step = DetailedTelegramCalendar(
        calendar_id="Arate", min_date=date.today()
    ).build()
    bot.send_message(chat_id, ARRIVAL_DATE)
    bot.send_message(chat_id, f"Select {LSTEP[step]}: ", reply_markup=calendar)


@bot.callback_query_handler(
    func=lambda call: DetailedTelegramCalendar.func(calendar_id="Arate")(call)
)
def handle_arrival_date_selection_rate(call):
    chat_id = call.message.chat.id
    try:
        result, key, step = DetailedTelegramCalendar(
            calendar_id="Arate", min_date=date.today()
        ).process(call.data)
        if not result and key:
            bot.edit_message_text(
                f"Select {LSTEP[step]}: ",
                chat_id,
                call.message.message_id,
                reply_markup=key,
            )
        elif result:
            user_data[chat_id]["arrival_date"] = str(result)
            bot.edit_message_text(
                f"You have selected arrival date: {result}",
                chat_id,
                call.message.message_id,
            )
            min_date = datetime.strptime(
                user_data[chat_id]["arrival_date"], "%Y-%m-%d"
            ).date() + timedelta(days=1)
            calendar, step = DetailedTelegramCalendar(
                calendar_id="Drate", min_date=min_date
            ).build()
            bot.send_message(chat_id, "Select departure date:")
            bot.send_message(chat_id, f"Select {LSTEP[step]}: ", reply_markup=calendar)
    except Exception:
        bot.send_message(chat_id, ERROR_UN)


@bot.callback_query_handler(
    func=lambda call: DetailedTelegramCalendar.func(calendar_id="Drate")(call)
)
def handle_departure_date_selection_rate(call):
    chat_id = call.message.chat.id
    try:
        min_date = datetime.strptime(
            user_data[chat_id]["arrival_date"], "%Y-%m-%d"
        ).date() + timedelta(days=1)
        result, key, step = DetailedTelegramCalendar(
            calendar_id="Drate", min_date=min_date
        ).process(call.data)
        if not result and key:
            bot.edit_message_text(
                f"Select {LSTEP[step]}: ",
                chat_id,
                call.message.message_id,
                reply_markup=key,
            )
        elif result:
            user_data[chat_id]["departure_date"] = str(result)
            bot.edit_message_text(
                f"You have selected departure date: {result}",
                chat_id,
                call.message.message_id,
            )
            count_hotel_rate(call.message)
    except Exception:
        bot.send_message(chat_id, ERROR_UN)


def count_hotel_rate(message):
    chat_id = message.chat.id
    key = ReplyKeyboardMarkup(row_width=5, one_time_keyboard=True, resize_keyboard=True)
    for num in range(1, 11):
        key.add(KeyboardButton(str(num)))
    msg = bot.send_message(chat_id, COUNT_HOTEL, reply_markup=key)
    bot.register_next_step_handler(msg, process_hotel_count_rate)


def process_hotel_count_rate(message):
    chat_id = message.chat.id
    try:
        hotel_count = int(message.text)
        user_data[chat_id]["hotel_count"] = hotel_count
        search_hotel_rate(message)
    except ValueError:
        msg = bot.send_message(chat_id, ERROR_VALUE)
        bot.register_next_step_handler(msg, process_hotel_count_rate)
    except Exception:
        bot.send_message(chat_id, ERROR_UN)


def search_hotel_rate(message):
    chat_id = message.chat.id

    dest_id = user_data[chat_id].get("dest_id")
    arrival_date = user_data[chat_id].get("arrival_date")
    departure_date = user_data[chat_id].get("departure_date")
    hotel_count = user_data[chat_id].get("hotel_count")
    city_name = user_data[chat_id].get("city_name")

    if dest_id and arrival_date and departure_date:
        QUERY_HOTEL_RATE["dest_ids"] = dest_id
        QUERY_HOTEL_RATE["arrival_date"] = arrival_date
        QUERY_HOTEL_RATE["departure_date"] = departure_date

        try:
            response = requests.get(URL_HOTEL, headers=HEADERS, params=QUERY_HOTEL_RATE)
            response.raise_for_status()
            hotels = response.json()

            if not hotels.get("result"):
                bot.send_message(chat_id, NOT_FIND)
                return

            hotel_list = hotels["result"][:hotel_count]

            for hotel in hotel_list:
                key = InlineKeyboardMarkup(row_width=1)
                key_url = InlineKeyboardButton(KEY_URL, url=hotel["url"])
                key_photo = InlineKeyboardButton(
                    KEY_PHOTO, callback_data="photo_rate" + str(hotel["hotel_id"])
                )
                key.add(key_url)
                key.add(key_photo)

                rating = hotel.get("review_score")
                if rating is None:
                    rating = "No rating"
                else:
                    rating = f"{rating}/10"

                bot.send_photo(
                    chat_id,
                    hotel["main_photo_url"].replace("square60", "square200"),
                    caption=HOTEL.format(
                        hotel["hotel_name"],
                        hotel["address"],
                        rating,
                        round(hotel["min_total_price"], 2),
                    ),
                    reply_markup=key,
                )

            save_query(
                chat_id=chat_id,
                city_name=city_name,
                hotel_count=hotel_count,
                arrival_date=arrival_date,
                departure_date=departure_date,
                query_dict=QUERY_HOTEL_RATE,
            )

        except requests.RequestException:
            bot.send_message(chat_id, ERROR_HOTEL)
        except Exception:
            bot.send_message(chat_id, ERROR_UN)
    else:
        bot.send_message(chat_id, REPEAT_FIND)


@bot.callback_query_handler(func=lambda call: call.data.startswith("photo_rate"))
def handle_photo_rate(call):
    photos = []
    chat_id = call.message.chat.id
    QUERY_PHOTO["hotel_ids"] = str(call.data[len("photo_rate") :])
    try:
        response = requests.get(URL_PHOTO, headers=HEADERS, params=QUERY_PHOTO)
        response.raise_for_status()
        photo = response.json()
        for ph in range(len(photo["data"][QUERY_PHOTO["hotel_ids"]])):
            photos.append(
                photo["url_prefix"] + photo["data"][QUERY_PHOTO["hotel_ids"]][ph][4]
            )
        for p in range(5):
            bot.send_photo(chat_id, photos[p])
    except requests.RequestException:
        bot.send_message(chat_id, ERROR_PHOTO)
    except Exception:
        bot.send_message(chat_id, ERROR_UN)
