'''This module contains the logic to seed the development databases
for the `Cat's Rare Treasures` FastAPI app.'''
from seed import seed_db
import os

try:
    if os.environ.get('DEV') == 'True':
        seed_db('dev')
    else:
        seed_db('test')
except Exception as e:
    print(e)
    raise e
