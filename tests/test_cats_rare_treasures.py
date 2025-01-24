'''This module contains the test suite for the
`Cat's Rare Treasures` FastAPI app.'''

from fastapi.testclient import TestClient
import pytest
from db.connection import connect_to_db, close_connection
from db.seed import seed_db
from main import app

@pytest.fixture
def reset_db(autouse=True):
    test_db = connect_to_db()
    seed_db()
    close_connection(test_db)

@pytest.fixture
def test_client():
    testclient = TestClient(app)
    return testclient

@pytest.fixture
def single_treasure():
    return {
      "treasure_name": "treasure-a",
      "colour": "turquoise",
      "age": 200,
      "cost_at_auction": "20.00",
      "shop": "shop-b"
    }

@pytest.fixture
def update_treasure():
    return {
      "cost_at_auction": 40.00
      
    }

@pytest.mark.skip
class TestGetTreasures:
    def test_get_tresures_returns_list(self, reset_db,test_client):
        response = test_client.get('/api/treasures').json()
        assert isinstance(response, dict)
    
    def test_get_tresures_returns_true_attributes(self,reset_db, test_client):
        respnse = test_client.get('/api/treasures').json()
        
        response_treasures = respnse['treasures']
        print( response_treasures)
        assert isinstance(response_treasures[0]['treasure_id'],int)
        assert isinstance(response_treasures[0]['treasure_name'],str)
        assert isinstance(response_treasures[0]['colour'],str)
        assert isinstance(response_treasures[0]['age'],int)
        assert isinstance(response_treasures[0]['cost_at_auction'],float)
        assert isinstance(response_treasures[0]['shop_id'],int)

    def test_get_treasures_has_typical_values(self, reset_db, test_client):
        respnse = test_client.get('/api/treasures').json()
        response_treasures = respnse['treasures']

        assert response_treasures[0]['treasure_id'] == 19
        assert response_treasures[0]['treasure_name'] == "treasure-q"
        assert response_treasures[0]['colour'] == "magenta"
        assert response_treasures[0]['age'] == 1
        assert response_treasures[0]['cost_at_auction'] == 60.99

    def test_get_treasures_sorted_ascending(self, reset_db, test_client):
        respnse = test_client.get('/api/treasures').json()
        response_treasures = respnse['treasures']

        for i in range(len(response_treasures)-1):
            assert response_treasures[i]['age'] <= response_treasures[i+1]['age']
        
    def test_get_treasures_sort_by_search_query(self, reset_db, test_client):
        respnse = test_client.get('/api/treasures?sort_by=cost_at_auction').json()
        response_treasures = respnse['treasures']

        for i in range(len(response_treasures)-1):
            assert response_treasures[i]['cost_at_auction'] <= response_treasures[i+1]['cost_at_auction']
        respnse = test_client.get('/api/treasures?sort_by=colour').json()
        response_treasures = respnse['treasures']

        for i in range(len(response_treasures)-1):
            assert response_treasures[i]['colour'] <= response_treasures[i+1]['colour']
            
    def test_get_treasures_orders_items_in_descending_order_with_query(self, reset_db, test_client):
        respnse = test_client.get('/api/treasures?sort_by=cost_at_auction&order=DESC').json()
        response_treasures = respnse['treasures']

        for i in range(len(response_treasures)-1):
            assert response_treasures[i]['cost_at_auction'] >= response_treasures[i+1]['cost_at_auction']
            
        respnse = test_client.get('/api/treasures?sort_by=colour&order=DESC').json()
        response_treasures = respnse['treasures']

        for i in range(len(response_treasures)-1):
            assert response_treasures[i]['colour'] >= response_treasures[i+1]['colour']

    def test_get_treasures_resturns_422_for_incorrect_query(self, reset_db, test_client):
        response = test_client.get('/api/treasures?sort_by=colur&order=DESC')
        assert response.status_code == 422
        
        
    def test_get_treasures_returns_404_for_bad_enpoint(self, reset_db, test_client):
        response = test_client.get('/hello/world')
        assert response.status_code == 404
        
    def test_get_treasures_returns_by_color_query(self, reset_db, test_client):
        response = test_client.get('/api/treasures?colour=gold')
        assert response.status_code == 200
        
    def test_handles_all_queries(self, reset_db, test_client):
        response = test_client.get('/api/treasures?sort_by=colour&colour=gold')
        assert response.status_code == 200
        
@pytest.mark.skip
class TestPostTreasures:
    def test_post_treasures_returns_201_on_success(self, test_client, single_treasure):
        response = test_client.post('/api/treasures', json=single_treasure)
        # print(response)
        assert response.status_code == 201
        
    def test_response_from_post_treasures_is_correct(self, test_client,single_treasure):
        response = test_client.post('/api/treasures', json=single_treasure)
        print(response.json()) 
        #assert response.json() == single_treasure
        assert response.json()['treasure_name'] == "treasure-a" 
        assert response.json()['colour'] == "turquoise" 
        assert response.json()['age'] == 200 
        assert response.json()['cost_at_auction'] == 20.00
        assert isinstance(response.json()['shop_id'],int)
    


    def test_response_from_patch_treasures_is_correct(self, test_client,update_treasure,reset_db):
        response = test_client.patch('/api/treasures/2', json=update_treasure)
        print(response.json())
        assert response.status_code == 200
        assert response.json()[0]['cost_at_auction'] != response.json()[1]['cost_at_auction']
    
    def test_response_from_delete_treasures_is_correct(self, test_client,reset_db):
        response = test_client.delete('/api/treasure/2')
        assert response.status_code == 200
        assert response.json()["treasure_id"] != 2

class TestShopsValues:
    def test_response_from_get_shops_is_correct(self, test_client,reset_db):
        response = test_client.get('/api/shops')
        #print(response)
        assert response.status_code == 200
        assert isinstance(response.json()[0]["shop_id"],int)

    def test_response_from_get_shops_has_correct_stock_value(self, test_client,reset_db):
        response = test_client.get('/api/shops')
        #print(response.json())
        assert response.json()[0]['stock_value'] 
        assert isinstance(response.json()[0]['stock_value'],float)
    
    def test_response_from_get_shops_(self, test_client,reset_db):
        response = test_client.get('/api/treasures?max_age=5&min_age=1')
        print(response.json())
        assert 0
    