import json
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from settings.loader import bot
from database.database import UserQuery
from settings.constants import (
    HISTORY,
    ERROR_HISTORY,
    ERROR_UN,
    KEY_LOWPRICE,
    KEY_BESTDEAL,
    KEY_RATING,
    NOT_FIND,
    KEY_URL,
    HOTEL,
    KEY_PHOTO,
    ERROR_DATE,
)
from settings.loader import URL_HOTEL, HEADERS


def show_history(message):
    chat_id = message.chat.id

    try:
        last_queries = (
            UserQuery.select()
            .where(UserQuery.chat_id == chat_id)
            .order_by(UserQuery.id.desc())
            .limit(5)
        )

        markup = InlineKeyboardMarkup()

        for query in last_queries:

            query_dict = json.loads(query.query)
            order_by = query_dict.get("order_by", "")

            if order_by == "price":
                query_type = KEY_LOWPRICE
            elif order_by == "distance":
                query_type = KEY_BESTDEAL
            elif order_by == "review_score":
                query_type = KEY_RATING
            else:
                query_type = "Unknown"

            button_text = (
                f"{query.city_name} - {query_type}: {query.hotel_count} hotels"
            )
            callback_data = f"repeat_query_{query.id}"
            button = InlineKeyboardButton(button_text, callback_data=callback_data)

            markup.add(button)

        bot.send_message(chat_id, HISTORY, reply_markup=markup)

    except UserQuery.DoesNotExist:
        bot.send_message(chat_id, ERROR_HISTORY)
    except Exception:
        bot.send_message(chat_id, ERROR_UN)


@bot.callback_query_handler(func=lambda call: call.data.startswith("repeat_query_"))
def handle_repeat_query(call):
    chat_id = call.message.chat.id
    query_id = int(call.data[len("repeat_query_"):])

    try:
        query = UserQuery.get(UserQuery.id == query_id)
        hotel_count = query.hotel_count
        query_dict = json.loads(query.query)
        order_by = query_dict.get("order_by", "")

        if order_by == "price":
            response = requests.get(URL_HOTEL, headers=HEADERS, params=query_dict)
            response.raise_for_status()
            hotels = response.json()
            if not hotels.get("result"):
                bot.send_message(chat_id, NOT_FIND + ERROR_DATE)
                return

            hotel_list = hotels["result"][:hotel_count]
            for hotel in hotel_list:
                key = InlineKeyboardMarkup(row_width=1)
                key_url = InlineKeyboardButton(KEY_URL, url=hotel["url"])
                key_photo = InlineKeyboardButton(
                    KEY_PHOTO, callback_data="photo_low" + str(hotel["hotel_id"])
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

        elif order_by == "distance":
            response = requests.get(URL_HOTEL, headers=HEADERS, params=query_dict)
            response.raise_for_status()
            hotels = response.json()
            if not hotels.get("result"):
                bot.send_message(chat_id, NOT_FIND + ERROR_DATE)
                return

            hotel_list = hotels["result"][:hotel_count]
            for hotel in hotel_list:
                key = InlineKeyboardMarkup(row_width=1)
                key_url = InlineKeyboardButton(KEY_URL, url=hotel["url"])
                key_photo = InlineKeyboardButton(
                    KEY_PHOTO, callback_data="photo_dist" + str(hotel["hotel_id"])
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
        elif order_by == "review_score":
            response = requests.get(URL_HOTEL, headers=HEADERS, params=query_dict)
            response.raise_for_status()
            hotels = response.json()
            if not hotels.get("result"):
                bot.send_message(chat_id, NOT_FIND + ERROR_DATE)
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
    except UserQuery.DoesNotExist:
        bot.send_message(chat_id, ERROR_HISTORY)
    except Exception:
        bot.send_message(chat_id, ERROR_UN)
