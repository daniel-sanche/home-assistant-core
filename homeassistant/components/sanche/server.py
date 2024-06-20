from flask import Flask, request
import pymongo

app = Flask(__name__)

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["lifeline"]
timeline_collection = db["timeline"]
# add indices
timeline_collection.create_index("start_time")
timeline_collection.create_index("entity_id")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/new_data', methods=['POST'])
def new_data():
    data = request.get_json()
    entity_id = data['entity_id']
    # find most recent entry for entity_id
    most_recent = timeline_collection.find_one(sort=[("start_time", pymongo.DESCENDING)])
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

if __name__ == '__main__':
    port = 7070
    app.run(host='0.0.0.0', port=port)
    # start mongo with:
    # docker run -p 27017:27017 -it mongo:latest
