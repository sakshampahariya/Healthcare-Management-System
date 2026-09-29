class APIError(Exception):
    status_code = 400
    code = "BAD_REQUEST"
    message = "Bad request"

    def __init__(self, message: str | None = None, code: str | None = None):
        super().__init__(message or self.message)
        if message:
            self.message = message
        if code:
            self.code = code

    def to_dict(self) -> dict:
        return {
            "success": False,
            "error": {"code": self.code, "message": self.message},
        }


class BadRequestError(APIError):
    status_code = 400
    code = "BAD_REQUEST"
    message = "Bad request"


class UnauthorizedError(APIError):
    status_code = 401
    code = "UNAUTHORIZED"
    message = "Authentication required"


class ForbiddenError(APIError):
    status_code = 403
    code = "FORBIDDEN"
    message = "You do not have access to this resource"


class NotFoundError(APIError):
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found"


class ConflictError(APIError):
    status_code = 409
    code = "CONFLICT"
    message = "Resource conflict"


class UnprocessableEntityError(APIError):
    status_code = 422
    code = "UNPROCESSABLE_ENTITY"
    message = "Request could not be processed"
