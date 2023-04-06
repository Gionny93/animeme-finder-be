from application import app, db, fetch_data, utils, log_info, status_dict, api_version
from flask import request, jsonify
from bson import json_util, ObjectId
import json
import asyncio
from application.utils import handle_exceptions
from flask_login import login_required, current_user

# API used by frontend to fetch recommended anime and other anime related actions


# /login call returns the user_id which is needed by the frontend to call protected apis, 
# example curl -H "Authorization: 642f302de82db80238da927c" 
#              -d '[{"title": "test1", "score": 4, "user": "gionny"}, {"title": "test2", "score": 8, "user": "gionny"}]' 
#              -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/api/v1/anime-list

@app.route(f"/api/v{api_version}/anime-list", methods=["POST", "PUT"])
@login_required
@handle_exceptions
def add_anime_list():
    # body json format expected [{"tile": title1, "score", 10, "user": user}, ...]

    log_info(f"CURRENT USER -> {current_user}")

    if not current_user:
        return jsonify({"error": "Unauthorized"}), status_dict["UNAUTHORIZED"]

    response = request.get_json()

    if request.method == "POST":

        # existing_user_list = db.user_anime_list.find_one({"user_id": logged_in_user_id})

        # if existing_user_list:
        #     return jsonify({"message": "You have already added your anime list"}), status_dict["KO"]

        db.user_anime_list.insert_many(response)
        return jsonify({"message": "Anime list added successfully"}), status_dict["OK"]

    if request.method == "PUT":
        for anime in response:
            title = anime["title"]
            updated_data = {"$set": anime}
            db.user_anime_list.update_many({"title": title}, updated_data)
        return jsonify({"message": "Anime list updated successfully"}), status_dict["OK"]

@app.route("/")




# @app.route("/anime_data")
# def populate_db_all_anime():

#     f = open("anime_cache.json")

#     cache_data = json.load(f)

#     all_data = cache_data['sfw'] + cache_data['nsfw']

#     f.close()

#     all_anime_ids_chunks = utils.chunks([f"https://api.jikan.moe/v4/anime/{anime_id}/full" for anime_id in all_data], 60)

#     for idx, chunk in enumerate(all_anime_ids_chunks):
#         anime_data = fetch_data.fetch_anime_data(chunk)

#         print(f"Inserting DB... chunk #{idx+1}")

#         try:
#             db.anime_list.insert_many(parse_json(anime_data))
#         except:
#             print(f"chunk # {idx+1} has problems!")
            

#     # loop = asyncio.new_event_loop()
#     # anime_data = loop.run_until_complete(fetch_data.fetch_anime_data(episodes))
#     # loop.close()


#     return {"status": "OK"}

@app.route(f"/api/v{api_version}/search_anime/<anime_name>") 
def get_anime(anime_name):
    return parse_json(db.anime_list_test.find({"title": anime_name}, {"_id": 0}))

@app.route(f"/api/v{api_version}/add_watchlist", methods=["POST"])
def add_anime_to_watchlist():
    response = request.get_json()
    db.test_flask.insert_one({
        "name": response["name"],
        "surname": "LUL"
    })
    return response

def parse_json(data):
    return json.loads(json_util.dumps(data))