from flask_httpauth import HTTPTokenAuth


from models.user import User

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    return User.objects(auth_token=token).first()