from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/new_data', methods=['POST'])
def new_data():
    data = request.get_json()
    print(data)
    return data

if __name__ == '__main__':
    port = 7070
    app.run(host='0.0.0.0', port=port)
