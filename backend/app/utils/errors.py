from flask import jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message, status_code=None, code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.message = message


def error_response(message, status_code=400, code="bad_request"):
    response = jsonify({"error": {"code": code, "message": message}})
    response.status_code = status_code
    return response


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return error_response(error.message, error.status_code, error.code)

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        message = error.description if error.code < 500 else "Unexpected server error."
        return error_response(message, error.code, error.name.lower().replace(" ", "_"))

    @app.errorhandler(Exception)
    def handle_unexpected_error(_error):
        return error_response("Unexpected server error.", 500, "internal_server_error")
