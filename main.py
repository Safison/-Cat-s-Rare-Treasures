'''This module is the entrypoint for the `Cat's Rare Treasures` FastAPI app.'''
from fastapi import FastAPI, HTTPException
from db.connection import connect_to_db, close_connection
import pg8000.native 
from pg8000.native import Connection, identifier, literal, DatabaseError
from utils import add_colour_condition
from pydantic import BaseModel

app = FastAPI()


@app.get('/api/treasures')
def get_treasures(sort_by = 'age', order='ASC', colour = None):
    conn = None
    try:
        conn = connect_to_db()
        where_colour = ''
        if colour:
            where_colour = f"WHERE colour={literal(colour)}"
        query_string = f"SELECT * FROM treasures {where_colour} ORDER BY {identifier(sort_by)} {identifier(order)}"
        # if colour:
        #     query_string = add_colour_condition(query_string, colour)
        #     #query_string = f"SELECT * FROM treasures ORDER BY {identifier(sort_by)} {identifier(order)} WHERE colour = {identifier(colour)}"
        print (query_string)
        tresures_list = conn.run(query_string)
        treasure_col = [col['name'] for col in conn.columns]
        result = []
        for treasure in tresures_list:
            result.append(dict(zip(treasure_col,treasure)))
        formated_treasures = {'treasures': result}
        return formated_treasures
    except DatabaseError as e:
        print ('>>>>>>>>>>>>>',e)
        raise HTTPException(status_code=422, detail="We have been unable to process your request, please check your input",)
    except Exception:
        raise HTTPException(status_code=500, detail="Whoops, something went wrong, please try again.")
    finally:
        if conn:
            close_connection(conn)

class Treasure(BaseModel):
    treasure_name:str
    colour:str
    age:int
    cost_at_auction:float
    shop:str
    
@app.post('/api/treasures', status_code=201)
def post_treasure(treasure:Treasure):
    conn = None
    try:
        conn = connect_to_db()
        
        shop_id = f"SELECT shop_id FROM shops WHERE shop_name = {(treasure.shop)}"
        print(shop_id)
        
        query = "INSERT INTO treasures (treasure_name, colour, age, cost_at_auction, shop_id)"
        query += " VALUES (:treasure_name, :colour, :age, :cost_at_auction, :shop_id) RETURNING *"
        response = conn.run(query, **treasure.model_dump(), shop_id=shop_id)
        print('>>>', response)
    except:
        pass
    finally:
        if conn:
            close_connection(conn)