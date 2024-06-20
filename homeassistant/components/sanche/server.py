from flask import Flask, request
import pymongo

app = Flask(__name__)

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["events"]

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/new_data', methods=['POST'])
def new_data():
    data = request.get_json()
    entity_id = data['entity_id']
    x = db[entity_id].insert_one(data)

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
