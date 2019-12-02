from flask import Blueprint, g
from flask_httpauth import HTTPTokenAuth
from flask import request, abort, jsonify
from simple_auth_service import users

bp = Blueprint("vehicle", __name__, url_prefix="/vehicle")
auth = HTTPTokenAuth()


@auth.verify_token
def verify_token(token):
    data = users.verify_auth_token(token)
    if not data:
        return False
    if not "action" in data or data["action"] != "access":
        return False
    return ("permissions" in data) and ("vehicles" in data["permissions"])


# This would be an exampe of a business logic which is protected by
# authentication and authorization. All methods here are accesible only
# to users with 2FA.
# Also:
# - This code can be in a separate microservice
# - Since we rely on client tokens access to users/token db is no needed
@bp.route("/drive", methods=["GET"])
@auth.login_required
def drive():
    return "vroom vroom vroom"
