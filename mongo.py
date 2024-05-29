import json
from pymongo.mongo_client import MongoClient
from urllib.parse import quote_plus

with open('config.json') as f:
    config = json.load(f)

mongo_user = config['mongodb']['username']
mongo_pass = quote_plus(config['mongodb']['password'])  # Encode password
uri = f"mongodb+srv://{mongo_user}:{mongo_pass}@rindangdb.cefqbq4.mongodb.net/?retryWrites=true&w=majority&appName=rindangDB"
# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)