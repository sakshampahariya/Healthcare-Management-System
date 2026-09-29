from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import User
from app.services import auth_service
from app.utils.decorators import current_user_id
from app.utils.errors import UnauthorizedError
from app.utils.responses import success_response
from app.utils.validators import json_body

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/signup")
def signup():
    user = auth_service.signup(json_body())
    return success_response(user.to_dict(), status=201)


@auth_bp.post("/login")
def login():
    user, token = auth_service.login(json_body())
    return success_response({"access_token": token, "user": user.to_dict()})


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, current_user_id())
    if user is None:
        raise UnauthorizedError("User no longer exists", "USER_NOT_FOUND")
    return success_response(user.to_dict())
