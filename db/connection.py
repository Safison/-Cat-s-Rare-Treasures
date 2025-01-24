from pg8000.native import Connection
from dotenv import load_dotenv
import os

path = '.dev.env' if os.environ.get('DEV') == 'True' else '.env'
print(path)
load_dotenv(dotenv_path=path)


def connect_to_db():
    return Connection(
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        database=os.getenv("PG_DATABASE"),
        host=os.getenv("PG_HOST"),
        port=int(os.getenv("PG_PORT"))
    )

def close_connection(db):
    db.close() 
