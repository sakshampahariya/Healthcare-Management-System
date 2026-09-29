import logging
import os

from flask import Flask, request
from flask_jwt_extended.exceptions import JWTExtendedException
from flasgger import Swagger
from marshmallow import ValidationError as MarshmallowValidationError
from werkzeug.exceptions import HTTPException

from app.config import config_by_name
from app.extensions import db, init_celery, jwt, mail, migrate
from app.services.cache_service import init_redis
from app.utils.errors import APIError, UnprocessableEntityError
from app.utils.responses import error_response

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "EVE Diagnostic Booking API",
        "description": "REST API for diagnostic test booking and simulated payments.",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT access token. Example: Bearer eyJ...",
        }
    },
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs",
}


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    env_name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(env_name, config_by_name["default"]))

    _configure_cors(app)
    _configure_logging(app)
    _register_extensions(app)
    _register_error_handlers(app)

    from app.routes import register_blueprints

    register_blueprints(app)

    # Register Celery tasks with the worker.
    from app.tasks import payment_tasks  # noqa: F401

    return app


def _configure_logging(app: Flask) -> None:
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logging.getLogger("werkzeug").setLevel(logging.INFO)


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    init_celery(app)
    init_redis(app)
    Swagger(app, template=swagger_template, config=swagger_config)

    from app import models  # noqa: F401

    @jwt.unauthorized_loader
    def missing_token(reason):
        return error_response("UNAUTHORIZED", "Authentication required", 401)

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return error_response("INVALID_TOKEN", "Invalid or malformed token", 401)

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return error_response("TOKEN_EXPIRED", "Access token has expired", 401)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(APIError)
    def handle_api_error(err: APIError):
        return error_response(err.code, err.message, err.status_code)

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow(err: MarshmallowValidationError):
        return error_response("VALIDATION_ERROR", "Invalid request payload", 422)

    @app.errorhandler(UnprocessableEntityError)
    def handle_unprocessable(err: UnprocessableEntityError):
        return error_response(err.code, err.message, err.status_code)

    @app.errorhandler(JWTExtendedException)
    def handle_jwt(err: JWTExtendedException):
        return error_response("UNAUTHORIZED", str(err), 401)

    @app.errorhandler(HTTPException)
    def handle_http(err: HTTPException):
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
        }
        return error_response(
            code_map.get(err.code, "HTTP_ERROR"),
            err.description or "Request failed",
            err.code or 500,
        )

    @app.errorhandler(Exception)
    def handle_unexpected(err: Exception):
        app.logger.exception("Unhandled error: %s", err)
        return error_response("INTERNAL_SERVER_ERROR", "An unexpected error occurred", 500)


def _configure_cors(app: Flask) -> None:
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            return response

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response
