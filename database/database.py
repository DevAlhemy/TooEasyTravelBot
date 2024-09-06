import peewee
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "database.sqlite3")

db = peewee.SqliteDatabase(db_path)


class UserQuery(peewee.Model):
    chat_id = peewee.IntegerField()
    city_name = peewee.CharField()
    hotel_count = peewee.IntegerField()
    arrival_date = peewee.DateField()
    departure_date = peewee.DateField()
    query = peewee.TextField()

    class Meta:
        database = db
        db_table = "user_queries"


def create_table():
    db.connect()
    if not UserQuery.table_exists():
        db.create_tables([UserQuery])
    db.close()


def save_query(
    chat_id,
    city_name=None,
    hotel_count=None,
    arrival_date=None,
    departure_date=None,
    query_dict=None,
):
    query_json = json.dumps(query_dict) if query_dict else None

    UserQuery.create(
        chat_id=chat_id,
        city_name=city_name,
        hotel_count=hotel_count,
        arrival_date=arrival_date,
        departure_date=departure_date,
        query=query_json,
    )

    user_queries = (
        UserQuery.select()
        .where(UserQuery.chat_id == chat_id)
        .order_by(UserQuery.id.asc())
    )
    if user_queries.count() > 5:
        excess_queries = user_queries.count() - 5
        for query in user_queries.limit(excess_queries):
            query.delete_instance()
