# from model import anime
# import aiohttp
# import asyncio
import requests
from time import sleep
from bson import json_util, ObjectId
import os
import json

from pymongo import MongoClient

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@gionny-cluster.0te89xo.mongodb.net/?retryWrites=true&w=majority"

mongodb_client = MongoClient(MONGO_URI)
db = mongodb_client.db

def fetch_anime_data(urls):
    anime_data = []
    for idx, url in enumerate(urls):
        url_to_download = url
        r = requests.get(url_to_download)

        try:
            data = r.json()["data"]
            filtered_response = {
                "trailer_url": data["trailer"]["url"],
                "url": data["url"],
                "title": data["title"],
                "type": data["type"],
                "episodes": data["episodes"],
                "airing": data["airing"],
                "score": data["score"],
                "rank": data["rank"],
                "popularity": data["popularity"],
                "members": data["members"],
                "favorites": data["favorites"],
                "synopsis": data["synopsis"],
                "year": data["year"],
                "genres": data["genres"],
                "theme": data["theme"],
                "streaming": data["streaming"]
            }

            anime_data.append(filtered_response)

            print(f"ANIME #{idx+1} DOWNLOADED!")
        except Exception as e:
            print(f"There was an exception with the request {e.__class__}")
            with open("anime_download_error", "a") as f:
                f.write(str(url_to_download) + "\n")
        sleep(1)

    return anime_data
    
def parse_json(data):
    return json.loads(json_util.dumps(data))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if __name__ == "__main__":
    f = open("anime_cache.json")

    cache_data = json.load(f)

    all_data = cache_data['sfw'] + cache_data['nsfw']

    f.close()

    all_anime_ids_chunks = chunks([f"https://api.jikan.moe/v4/anime/{anime_id}/full" for anime_id in all_data], 60)

    for idx, chunk in enumerate(all_anime_ids_chunks):
        anime_data = fetch_anime_data(chunk)

        print(f"Inserting DB... chunk #{idx+1}")

        try:
            db.anime_list.insert_many(parse_json(anime_data))
        except Exception as e:
            print(f"chunk # {idx+1} has problems! {e}")
    
# async def get(url, session):
#     try:
#         async with session.get(url=url) as response:
#             response = await response.json()
#             data = response["data"]
#             filtered_response = {
#                 "trailer_url": data["trailer"]["url"],
#                 "url": data["url"],
#                 "title": data["title"],
#                 "type": data["type"],
#                 "episodes": data["episodes"],
#                 "airing": data["airing"],
#                 "score": data["score"],
#                 "rank": data["rank"],
#                 "popularity": data["popularity"],
#                 "members": data["members"],
#                 "favorites": data["favorites"],
#                 "synopsis": data["synopsis"],
#                 "year": data["year"],
#                 "genres": data["genres"],
#                 "theme": data["theme"],
#                 "streaming": data["streaming"]
#             }
#             return filtered_response
#             # return response
#             # print(f"Response -> {resp['title']}")
#     except Exception as e:
#         print(f"Unable to get url {url} due to {e.__class__}")


# # async def fetch_anime_data(urls):
# #     async with aiohttp.ClientSession() as session:
# #         return await asyncio.gather(*[get(url, session) for url in urls])

# # sleeping 1 sec because the api has a limit of 60 calls per minute
# async def fetch_anime_data(urls):
#     async with aiohttp.ClientSession() as session:
#         anime_data = []
#         for url in urls:
#             anime = await asyncio.gather(get(session, url))
#             anime_data.append(anime)
            
#             await asyncio.sleep(1)
#         return anime_data