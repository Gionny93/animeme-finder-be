from functools import wraps
from flask import jsonify
from application import log_info

def handle_exceptions(f):
    @wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            log_info(f"Error: {e}")
            return jsonify({"error": "An error occurred while processing the request"}), 500

    return func
