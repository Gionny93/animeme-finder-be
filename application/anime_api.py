from application import app, db, fetch_data, utils, log_info, status_dict, api_version
from flask import request, jsonify
import asyncio
from application.utils import handle_exceptions, parse_json
from flask_login import login_required, current_user

# API used by frontend to fetch recommended anime and other anime related actions

# TODO - JWT token instead of user_id in Authorization - Sessions timeout

# /login call returns the user_id which is needed by the frontend to call protected apis, 
# example curl -H "Authorization: 642f302de82db80238xxxx" 
#              -d '[{"title": "test1", "score": 4, "user": "gionny"}, {"title": "test2", "score": 8, "user": "gionny"}]' 
#              -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/api/v1/anime-list

@app.route(f"/api/v{api_version}/anime-list", methods=["POST", "PUT"])
@login_required
@handle_exceptions
def add_anime_list():
    # body json format expected [{"tile": title1, "score", 10, "user": user}, ...]

    req = request.get_json()

    if request.method == "POST":

        existing_user_list = db.user_anime_list.find_one({"user_id": current_user.username})

        if existing_user_list:
            return jsonify({"message": "You have already added your anime list"}), status_dict["KO"]

        db.user_anime_list.insert_many(req)
        return jsonify({"message": "Anime list added successfully"}), status_dict["OK"]

    if request.method == "PUT":
        for anime in req:
            title = anime["title"]
            updated_data = {"$set": anime}
            db.user_anime_list.update_many({"title": title}, updated_data)
        return jsonify({"message": "Anime list updated successfully"}), status_dict["OK"]


@app.route(f"/api/v{api_version}/search_anime/<anime_name>") 
@login_required
@handle_exceptions
def get_anime(anime_name):
    return parse_json(db.anime_list.find({"title": anime_name}, {"_id": 0}))


@app.route(f"/api/v{api_version}/watchlist", methods=["POST", "DELETE"])
@login_required
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


@handle_exceptions
@app.route(f"/api/v{api_version}/user-list/<user>", methods=["GET"])
def get_user_list(user):
    distinct_pipeline = [
    {"$match": {"user": user}},
    {"$group": {
        "_id": "$title",
        "doc": {"$first": "$$ROOT"}
    }},
    {"$replaceRoot": {"newRoot": "$doc"}},
    {"$project": {"_id": 0, "user": 0}}
]
    return parse_json(db.user_anime_list.aggregate(distinct_pipeline))

