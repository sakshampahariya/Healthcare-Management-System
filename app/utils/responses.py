from flask import jsonify


def success_response(data=None, meta=None, status: int = 200):
    payload = {"success": True, "data": data}
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status


def error_response(code: str, message: str, status: int):
    return jsonify({"success": False, "error": {"code": code, "message": message}}), status
