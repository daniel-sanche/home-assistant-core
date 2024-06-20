.PHONY: mongo server


server:
	PASSWORD=test USE_SSL=1 PORT=7070 MONGO_PORT=27017 python server.py

mongo:
	docker run -p 27017:27017 -it --name mongodb --rm mongo:latest

