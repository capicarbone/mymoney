

from mongoengine import DoesNotExist
from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth

from werkzeug.security import check_password_hash

from models.user import User

auth = HTTPTokenAuth(scheme='Bearer')
basic_auth = HTTPBasicAuth()


@basic_auth.verify_password
def verify_password(username, password):
    try:
        user = User.objects(email=username).get()
    except DoesNotExist:
        return None

    if check_password_hash(user.password_hash, password):
        return user

    return None


@auth.verify_token
def verify_token(token):
    return User.objects(auth_token=token).first()
