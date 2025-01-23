'''This module is the entrypoint for the `Cat's Rare Treasures` FastAPI app.'''
from fastapi import FastAPI, HTTPException
from db.connection import connect_to_db, close_connection
import pg8000.native 
from pg8000.native import Connection, identifier, literal, DatabaseError
from utils import add_colour_condition

app = FastAPI()


@app.get('/api/treasures')
def get_treasures(sort_by = 'age', order='ASC', colour=None):
    conn = None
    try:
        conn = connect_to_db()
        query_string = f"SELECT * FROM treasures ORDER BY {identifier(sort_by)} {identifier(order)}"
        if colour:
            query_string = add_colour_condition(query_string, colour)
        tresures_list = conn.run(query_string)
        treasure_col = [col['name'] for col in conn.columns]
        result = []
        for treasure in tresures_list:
            result.append(dict(zip(treasure_col,treasure)))
        formated_treasures = {'treasures': result}
        return formated_treasures
    except DatabaseError:
        raise HTTPException(status_code=422, detail="We have been unable to process your request, please check your input")
    except Exception:
        raise HTTPException(status_code=500, detail="Whoops, something went wrong, please try again.")
    finally:
        if conn:
            close_connection(conn)




