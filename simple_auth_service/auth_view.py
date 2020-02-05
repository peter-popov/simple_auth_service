from flask import Blueprint, request, abort, jsonify, url_for
from flask_httpauth import HTTPBasicAuth
from simple_auth_service import users

bp = Blueprint("auth", __name__, url_prefix="/auth")
auth = HTTPBasicAuth()


def verify_token(token, expected_action):
    data = users.verify_auth_token(token)
    if not data:
        abort(403, "Invalid verification token")
    if not "action" in data or data["action"] != expected_action:
        abort(403, "Invalid verification token")
    user = users.get_user(data["id"])
    if not user:
        abort(400)
    return user


@auth.verify_password
def verify_password(username, password):
    user = users.get_user(username)
    if user:
        return user.verify_password(password)
    return False


@bp.route("/login", methods=["GET"])
@auth.login_required
def login():
    """User login endpoint
    For users with MFA, returns 403 and a token for making OTP validation
    For users without MFA, returns access_token with limited permissions(only set MFA)
    ---
    tags:
      - auth
    responses:
      200:
        description: All good, returns access_token
      403:
        description: User, password, or token are invalid. Or MFA is required
    """
    user = users.get_user(auth.username())

    if not user.email_verified:
        abort(403, "Please verify email")

    if user.mfa_device:
        return (
            jsonify(
                {
                    "message": "MFA required",
                    "mfa_token": user.generate_token(60, "mfa"),
                    "expires_in": 60,
                }
            ),
            403,
        )

    # If not MFA device is set we still allow the log in,
    # but we only permit to acesss to user info
    return jsonify({"access_token": user.generate_access_token(60), "expires_in": 60})


@bp.route("/mfa", methods=["POST"])
def mfa():
    """OTP validation for MFA
    ---
    tags:
      - auth
    parameters:
      - name: mfa_token
        description: Token returned by login API
        in: body
      - name: otp
        in: body
        description: One time passwords generated by user's OTP device. For sake of this project it's should be MFA device ID plus 17
    responses:
      200:
        description: All good, returns access_token
      403:
        description: User, password, or token are invalid. Or MFA is required
    """
    mfa_token = request.json.get("mfa_token")
    otp = request.json.get("otp")
    user = verify_token(mfa_token, "mfa")
    if not user.verify_otp(otp):
        abort(403, "Invalid password")

    return jsonify({"access_token": user.generate_access_token(60), "expires_in": 60})


@bp.route("/signup", methods=["POST"])
def signup():
    """Sign up a new user
    email will be used as user id
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: username
      - in: body
        name: password
      - in: body
        name: email
    responses:
      200:
        description: All good, verify your email
      403:
        description: User already exists
    """
    # Will use swagger to verify the schema... later
    username = request.json.get("username")
    password = request.json.get("password")
    email = request.json.get("email")

    user = users.add_user(username, password, email)
    if user is None:
        abort(403, description="User already exists")

    email_verify_token = user.generate_token(60, "email")
    email_verify_url = url_for(
        "auth.verify_email", token=email_verify_token, _external=True
    )

    # Imagine we send it by email:
    return jsonify({"username": user.username, "link_in_email": email_verify_url}), 201


@bp.route("/verify_email/<token>", methods=["GET"])
def verify_email(token):
    """Verify email
    ---
    tags:
      - auth
    parameters:
      - in: path
        name: token
    responses:
      200:
        description: All good, go to login
      403:
        description: Invalid token
    """
    user = verify_token(token, "email")
    user.email_verified = True
    users.update_user(user)
    return "Email Verified"


@bp.route("/resetpassword", methods=["GET"])
def init_reset_password():
    """Initialize password reset
    This API always returns a token... but in case of unknown user the token will be invalid
    ---
    tags:
      - auth
    responses:
      200:
        description: All good, check your email
    """
    email = request.json.get("email")
    user = users.get_user(email)
    # As with a real email, this method will always succeed in order to not reveal whether a user exists
    # In case if a user does not exists we will generate an invalid token
    token = None
    if user:
        token = user.generate_token(60, "set_password")
    else:
        token = users.User("", "", "").generate_token(60, "invalid")

    # Imagine we send it by email:
    return jsonify(
        {"link_in_email": url_for("auth.reset_password", token=token, _external=True)}
    )


@bp.route("/resetpassword/<token>", methods=["POST"])
def reset_password(token):
    """Reset password using link from email
    ---
    tags:
      - auth
    parameters:
      - in: path
        name: token
      - in: body
        name: new_password
    responses:
      200:
        description: All good, got to login
      403:
        description: Invalid token   
    """
    new_password = request.json.get("new_password")
    user = verify_token(token, "set_password")
    user.set_password(new_password)
    users.update_user(user)
    return "Success"
