from flask import Blueprint, g, request, abort, jsonify, url_for
from flask_httpauth import HTTPTokenAuth
from simple_auth_service import users

bp = Blueprint("user", __name__, url_prefix="/user")
auth = HTTPTokenAuth()


def verify_action(token, expected_action):
    data = users.verify_auth_token(token)
    if not data:
        abort(403, "Invalid verification tocken")
    if not "action" in data or data["action"] != expected_action:
        abort(403, "Invalid verification tocken")


@auth.verify_token
def verify_token(token):
    data = users.verify_auth_token(token)
    if not data:
        return False
    if not "action" in data or data["action"] != "access":
        return False
    # Usualy we can simply rely on the content of the token, but
    # for users managment it makes sense to load a user record in our case
    g.current_user = users.get_user(data["id"])
    return g.current_user != None


@bp.route("/profile", methods=["GET"])
@auth.login_required
def profile():
    return jsonify(g.current_user.__dict__)


@bp.route("/setmfadevice", methods=["GET"])
@auth.login_required
def init_set_mfa_device():
    user = g.current_user
    token = user.generate_token(60, "set_mfa_device")
    return jsonify(
        {"link_in_email": url_for("user.set_mfa_device", token=token, _external=True)}
    )


@bp.route("/setmfadevice/<token>", methods=["POST"])
@auth.login_required
def set_mfa_device(token):
    verify_action(token, "set_mfa_device")
    g.current_user.mfa_device = request.json.get("mfa_device")
    return "Success"
