'''This module is the entrypoint for the `Cat's Rare Treasures` FastAPI app.'''
from fastapi import FastAPI, HTTPException
from db.connection import connect_to_db, close_connection
import pg8000.native 
from pg8000.native import Connection, identifier, literal, DatabaseError
from utils import add_colour_condition
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()


@app.get('/api/treasures')
def get_treasures(sort_by = 'age', order='ASC', colour = None, max_age:int=None, min_age=None):
    conn = None
    try:
        conn = connect_to_db()
        where_queries = []
        where_string = ''
        if colour:
            where_queries.append(f"colour={literal(colour)}")
        if max_age:
            where_queries.append(f"age <= {literal(max_age)}")
        if min_age:
            where_queries.append(f"age >= {literal(min_age)}")
        if len(where_queries) >= 1:
            where_string = "WHERE " + ' AND '.join(where_queries)
        
        query_string = f"SELECT * FROM treasures {where_string} ORDER BY {identifier(sort_by)} {identifier(order)}"
        print(' and '.join(where_queries))
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
        shop_id_query = "SELECT shop_id FROM shops WHERE shop_name = :shop_name"
        shop_id = conn.run(shop_id_query, shop_name = treasure.shop)[0][0]
        query = "INSERT INTO treasures (treasure_name, colour, age, cost_at_auction, shop_id)"
        query += " VALUES (:treasure_name, :colour, :age, :cost_at_auction, :shop_id) RETURNING *"
        print(f"the query {query}")
        response = conn.run(query, **treasure.model_dump(), shop_id=shop_id)[0]
        treasure_col = [col['name'] for col in conn.columns]
        formated_treasure = dict(zip(treasure_col, response))
        return formated_treasure
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="We encountered a database error, please don't try again.")
    finally:
        if conn:
            close_connection(conn)

class Treasure(BaseModel):
    cost_at_auction:float
    
@app.patch('/api/treasures/{treasure_id}')
def update_price(treasure_id,treasure:Treasure):
    conn = None
    try:
        conn = connect_to_db()
        select_qstring = "SELECT cost_at_auction FROM treasures WHERE treasure_id = :treasure_id"
        original_price = conn.run(select_qstring, treasure_id=treasure_id)
        price_col = [col['name'] for col in conn.columns]
        formatted_price = dict(zip(price_col, original_price))
        query_string = """UPDATE treasures SET cost_at_auction = :cost_at_auction 
                    WHERE treasure_id = :treasure_id RETURNING cost_at_auction"""
        updated_treasure = conn.run(query_string, cost_at_auction=treasure.cost_at_auction, treasure_id=treasure_id)
        treasure_col = [col['name'] for col in conn.columns]
        formated_treasure = dict(zip(treasure_col, updated_treasure))
        price_list =[]
        price_list.append(formatted_price)
        price_list.append(formated_treasure)
        return price_list
    except DatabaseError:
        raise HTTPException(status_code=500, detail="An error occured, please try again")
    finally:
        if conn:
            close_connection(conn)
        
@app.delete ('/api/treasure/{treasure_id}')
def delete_treasure(treasure_id:int):
    conn = None
    try:
        conn = connect_to_db()
        select_qstring = "SELECT treasure_id FROM treasures WHERE treasure_id = :treasure_id"
        selected_treasure = conn.run(select_qstring, treasure_id=treasure_id)
        treasure_col = [col['name'] for col in conn.columns]
        formated_treasure = dict(zip(treasure_col, selected_treasure))
        query_string = "DELETE FROM treasures WHERE treasure_id = :treasure_id"
        conn.run(query_string, treasure_id = treasure_id)
        return formated_treasure
    except DatabaseError:
        raise HTTPException(status_code=500, detail="An error occured, please try again")
    finally:
        if conn:
            close_connection(conn)
            
@app.get ('/api/shops/')
def get_shops():
    conn = None
    try:
        conn = connect_to_db()
        query_string = "SELECT * FROM shops"
        shops_list = conn.run(query_string)
        shops_col = [col['name'] for col in conn.columns]
        result_list=[]
        for shop in shops_list:
            result_list.append(dict(zip(shops_col,shop)))
            new_query = "SELECT sum(cast (cost_at_auction as numeric)) FROM treasures WHERE shop_id=:shop_id"
            shop_id = shop[0]
            shop_cost = conn.run(new_query, shop_id=shop_id)[0][0]
            result_list[-1].update({'stock_value':shop_cost})
        return result_list
    except DatabaseError:
        raise HTTPException(status_code=500, detail="An error occured, please try again")
    finally:
        if conn:
            close_connection(conn)

    