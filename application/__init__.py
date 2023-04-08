from flask import Flask
import os
from pymongo import MongoClient
from model import anime
import logging
from datetime import timedelta

logging.basicConfig(level=logging.INFO)
log_info = logging.info

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
app.config["MONGO_URI"] = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@gionny-cluster.0te89xo.mongodb.net/?retryWrites=true&w=majority"

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

mongodb_client = MongoClient(app.config["MONGO_URI"])
db = mongodb_client.db

db.users.create_index("username", unique=True)

status_dict = {
    "OK": 200,
    "KO": 201,
    "ALREADY_ADDED": 202,
    "UNAUTHORIZED": 401,
    "GENERIC_ERROR": 400
}

api_version = 1


from application import anime_api, login_api, utils