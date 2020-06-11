
from flask_restful import Resource, fields, marshal_with
from api.authentication import basic_auth

user_fields = {
    'email': fields.String,
    'token': fields.String(attribute='auth_token')
}

class Login(Resource):
    method_decorators = [basic_auth.login_required]

    @marshal_with(user_fields)
    def post(self):
        return basic_auth.current_user()