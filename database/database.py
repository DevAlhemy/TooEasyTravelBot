import peewee
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
