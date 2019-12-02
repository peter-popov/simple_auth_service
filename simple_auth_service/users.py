from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)

SECRET_KEY = "Move Me To Proper Secret Manager"


class User(object):
    def __init__(self, username, password, email):
        self.userID = email  # uuid1()
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email
        self.email_verified = False
        # Very simple permission management
        self.permissions = ["vehicles"]
        self.mfa_device = None

    def generate_access_token(self, expiration):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        permissions = []  # If no mfa device only give access user's data(implicit)
        if self.mfa_device:
            permissions = self.permissions
        return s.dumps(
            {"id": self.userID, "action": "access", "permissions": permissions}
        ).decode("ascii")

    def generate_token(self, expiration, action):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({"id": self.userID, "action": action}).decode("ascii")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def verify_otp(self, otp):
        # OTP is device id plus 17
        return self.mfa_device and (self.mfa_device + 17 == otp)


user_db = {}


def add_user(username, password, email):
    user = User(username, password, email)
    if user.email in user_db:
        return None
    user_db[user.userID] = user
    return user


def get_user(userID):
    return user_db.get(userID, None)


def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        return s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token
