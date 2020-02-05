import os
import jsonpickle
import json
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)
from pymongo import MongoClient

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

    def jsonify(self):
        return jsonify(self.__dict__)


def to_dict(obj):
    return json.loads(jsonpickle.encode(obj))

def from_dict(d):
    del d["_id"]
    return jsonpickle.decode(json.dumps(d, default=lambda o: '<not serializable>'))

class UserMongoDB(object):
    def __init__(self):
        self.client = MongoClient(os.environ["MONGODB_HOSTNAME"],
                                   username=os.environ["MONGODB_USERNAME"], 
                                   password=os.environ["MONGODB_PASSWORD"])
        self.db = self.client[os.environ["MONGODB_DATABASE"]]
        self.users = self.db['users']
        
    def add_user(self, username, password, email):
        user = get_user(email)
        if user:
            return None
        user = User(username, password, email)
        self.users.insert_one(to_dict(user))
        return user

    def get_user(self, id):
        doc = self.users.find_one({"email": id})
        if not doc:
            return None
        return from_dict(doc)

    def update_user(self, user):
        self.users.update_one({"email": user.userID}, {"$set":to_dict(user)})

user_db = UserMongoDB()


def add_user(username, password, email):
    return user_db.add_user(username, password, email)


def get_user(id):
    return user_db.get_user(id)

def update_user(user):
    return user_db.update_user(user)


def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        return s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token
