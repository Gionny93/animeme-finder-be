from application import app, db, fetch_data, utils, log_info, status_dict, api_version
from flask import request, jsonify
import asyncio
from application.utils import handle_exceptions, parse_json
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime
from pandas import DataFrame
from algorithms.collaborative_filtering import CollFiltering
from functools import lru_cache

# API used by frontend to fetch recommended anime and other anime related actions

# TODO - https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens/

# example curl
'''
curl    -H "Authorization: Bearer xxx" 
        -d '[{"title": "test1", "score": 4}, {"title": "test2", "score": 8}]' -H "Content-Type: application/json" 
        -X POST http://127.0.0.1:5000/api/v1/anime-list
'''

@app.route(f"/api/v{api_version}/anime-list", methods=["POST", "PUT", "GET"])
@jwt_required()
@handle_exceptions
def anime_list():
    # body json format expected [{"tile": title1, "score", 10}, ...]

    if request.method == "POST":

        req = request.get_json()

        for r in req:
            r["user"] = get_jwt_identity()
            r["date_modified"] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        db.user_anime_list.insert_many(parse_json(req))
        return jsonify({"message": "Anime list added successfully"}), status_dict["OK"]

    if request.method == "PUT":
        req = request.get_json()
        for anime in req:
            title = anime["title"]
            updated_data = {"$set": anime}
            db.user_anime_list.update_many({"title": title}, updated_data)
        return jsonify({"message": "Anime list updated successfully"}), status_dict["OK"]

    # if request.method == "GET":
    #     get_anime_data() TODO paging

@lru_cache(maxsize=None)
def get_anime_data():
    return list(db.anime_list.find({}, {"_id": 0}).limit(20000))


@app.route(f"/api/v{api_version}/recommendation/", defaults={'num_recommended': 1})
@app.route(f"/api/v{api_version}/recommendation/<int:num_recommended>", methods=["GET", "POST"])
@jwt_required()
@handle_exceptions
def recommend_anime(num_recommended):
    algorithm = CollFiltering(DataFrame.from_dict(get_user_list(get_jwt_identity())), DataFrame.from_dict(get_anime_data()))
    res = algorithm.execute(top_n = num_recommended)
    return res.to_json(orient='records')



@app.route(f"/api/v{api_version}/anime", methods=["POST"]) 
@jwt_required()
@handle_exceptions
def get_anime():
    anime_name = request.get_json()
    return parse_json(db.anime_list.find({"title": anime_name['title']}, {"_id": 0}))

@app.route(f"/TEST", methods=["POST"]) 
@handle_exceptions
def get_genres_for_my_anime():
    anime_list = request.get_json()
    anime_genre = []

    for anime in anime_list:
        info = get_anime(anime["title"])[0]
        anime_genre.append({
            "title": info["title"], 
            "genre": [x["name"] for x in info["genres"]],
            "score": anime["score"]
        })

    return jsonify({"message": anime_genre}), status_dict["OK"]


@app.route(f"/api/v{api_version}/watchlist", methods=["POST", "DELETE"])
@jwt_required()
@handle_exceptions
def add_anime_to_watchlist():
    # request [{"anime_name": name}], post is probably going to be just 1, but delete can vary, maybe add frontend functionality to select anime to delete from user profile

    req = request.get_json()

    if request.method == "POST":
        db.user_anime_watchlist.insert_many(req)
        return jsonify({"message": "Anime watchlist updated successfully"}), status_dict["OK"]

    if request.method == "DELETE":
        anime_names_to_delete = [element["anime_name"] for element in req]
        db.user_anime_watchlist.delete_many({"anime_name": {"$in": anime_names_to_delete}})
        return jsonify({"message": "Anime watchlist updated successfully"}), status_dict["OK"]


@app.route(f"/api/v{api_version}/user-list/<user>", methods=["GET"])
@handle_exceptions
def get_user_list(user):
    distinct_pipeline = [
    {"$match": {"user": user}},
    {"$group": {
        "_id": "$title",
        "doc": {"$first": "$$ROOT"}
    }},
    {"$replaceRoot": {"newRoot": "$doc"}},
    {"$project": {"_id": 0}}
]
    return parse_json(db.user_anime_list.aggregate(distinct_pipeline))
