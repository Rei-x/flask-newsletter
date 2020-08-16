from flask import jsonify

error_codes = {
    "BadRequest": "Bad request",
    "InvalidEmail": "Invalid email",
    "AlreadySignedUp": "Email is already signed up",
    "Operational": "Operational error",
    "Unexpected": "Unexpected error",
    "DoesntExist": "Email doesn't exist",
    "BadCaptcha": "ReCaptcha error"
}


def error(error_code):
    return jsonify(success=False, error=error_codes.get(error_code, "Invalid error code"), error_code=error_code)
