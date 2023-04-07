from functools import wraps
from flask import jsonify
from bson import json_util
from application import log_info
import json

def handle_exceptions(f):
    @wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            log_info(f"Error: {e}")
            return jsonify({"error": "An error occurred while processing the request"}), 500

    return func


def parse_json(data):
    return json.loads(json_util.dumps(data))