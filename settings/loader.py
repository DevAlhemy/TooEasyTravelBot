from dotenv import load_dotenv, find_dotenv
from telebot import TeleBot
import os

if not find_dotenv():
    exit("File .env doesn't exist")
else:
    load_dotenv()

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_HOST = "apidojo-booking-v1.p.rapidapi.com"
URL_LOCATION = "https://apidojo-booking-v1.p.rapidapi.com/locations/auto-complete"
URL_HOTEL = "https://apidojo-booking-v1.p.rapidapi.com/properties/list"
URL_PHOTO = "https://apidojo-booking-v1.p.rapidapi.com/properties/get-hotel-photos"

bot = TeleBot(token=BOT_TOKEN)

HEADERS = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}

QUERY_LOCATION = {"text": "new york"}

QUERY_HOTEL_LOW = {
    "offset": "0",
    "arrival_date": "2023-10-10",
    "departure_date": "2023-10-15",
    "guest_qty": "1",
    "dest_ids": "20088325",
    "room_qty": "1",
    "search_type": "city",
    "order_by": "price",
}

QUERY_HOTEL_DIST = {
    "offset": "0",
    "arrival_date": "2023-10-10",
    "departure_date": "2023-10-15",
    "guest_qty": "1",
    "dest_ids": "20088325",
    "room_qty": "1",
    "search_type": "city",
    "order_by": "distance",
}

QUERY_HOTEL_RATE = {
    "offset": "0",
    "arrival_date": "2023-10-10",
    "departure_date": "2023-10-15",
    "guest_qty": "1",
    "dest_ids": "20088325",
    "room_qty": "1",
    "search_type": "city",
    "order_by": "review_score",
}

QUERY_PHOTO = {"hotel_ids": "59239"}
