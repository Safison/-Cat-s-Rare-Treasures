'''This module contains the test suite for the
`Cat's Rare Treasures` FastAPI app.'''

from fastapi.testclient import TestClient
import pytest
from db.connection import connect_to_db, close_connection
from db.seed import seed_db
from main import app

@pytest.fixture
def reset_db():
    test_db = connect_to_db()
    seed_db()
    close_connection(test_db)

@pytest.fixture
def test_client():
    testclient = TestClient(app)
    return testclient


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
        
        