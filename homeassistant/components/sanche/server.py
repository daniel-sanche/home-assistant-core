from flask import Flask, request
import pymongo
import os

app = Flask(__name__)

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["lifeline"]
timeline_collection = db["timeline"]
# add indices
timeline_collection.create_index("start_time")
timeline_collection.create_index("entity_id")

entity_cache = {}

@app.route('/')
def hello_world():
    return 'Hello, World!'

def require_password(func):
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if data is None or data.get('password') != app.config['PASSWORD']:
            return "ERROR: Unauthorized", 401
        return func(*args, **kwargs)
    return wrapper

def get_latest_entry(entity_id):
    latest = entity_cache.get(entity_id)
    if latest is None:
        latest = timeline_collection.find_one({"entity_id": entity_id}, sort=[("start_time", pymongo.DESCENDING)])
        entity_cache[entity_id] = latest
    return latest


@app.route('/new_data', methods=['POST'])
@require_password
def new_data():
    data = request.get_json()
    entity_id = data['entity_id']
    # find most recent entry for entity_id
    most_recent = get_latest_entry(entity_id)
    if most_recent is not None:
        if data["prev_uid"] != most_recent["_id"]:
            return "ERROR: prev_uid must match most recent entry", 400
        if data["start_time"] <= most_recent["start_time"]:
            return "ERROR: start_time must be greater than most recent entry", 400
    formatted_data = {
        "_id": data["uid"],
        "entity_id": data["entity_id"],
        "start_time": data["start_time"],
        "value": data["value"]
    }

    x = timeline_collection.insert_one(formatted_data)

    # print the size of the collection
    print(db[entity_id].count_documents({}))

    return "OK"

@app.route('/get_data', methods=['GET'])
def get_data():
    # print out database
    for collection in db.list_collection_names():
        print(collection)
        for x in db[collection].find():
            print(x)
    # return size of database
    return str(db.list_collection_names())

@app.route('/health', methods=['GET'])
def health():
    return "OK"

if __name__ == '__main__':
    password = os.environ.get('PASSWORD')
    if password is None:
        raise ValueError("PASSWORD environment variable not set")
    app.config['PASSWORD'] = password
    port = os.environ.get('PORT', 7070)
    # to generate ssl keys:
    # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    if os.environ.get('USE_SSL', False):
        if os.path.exists('cert.pem') and os.path.exists('key.pem'):
            print("Using SSL")
            app.run(host='0.0.0.0', port=7070, ssl_context=('cert.pem', 'key.pem'))
        else:
            raise ValueError("cert.pem or key.pem not found")
    else:
        app.run(host='0.0.0.0', port=port)
    # start mongo with:
    # docker run -p 27017:27017 -it mongo:latest
