'''This module is the entrypoint for the `Cat's Rare Treasures` FastAPI app.'''
from fastapi import FastAPI
from db.connection import connect_to_db, close_connection
import pg8000.native 
from pg8000.native import Connection, identifier, literal

app = FastAPI()


@app.get('/api/treasures')
def get_treasures(sort_by = 'age'):
    conn = connect_to_db()
    query_string = f"SELECT * FROM treasures ORDER BY {identifier(sort_by)}"
    tresures_list = conn.run(query_string)
    treasure_col = [col['name'] for col in conn.columns]
    result = []
    for treasure in tresures_list:
        result.append(dict(zip(treasure_col,treasure)))
    formated_treasures = {'treasures': result}
    close_connection(conn)  
    return formated_treasures




