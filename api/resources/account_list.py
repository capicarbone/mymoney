
from typing import List
from flask_restful import Resource, marshal_with, fields, reqparse
from api.authentication import auth
from models.account import Account

account_fields = {
    'id': fields.String,
    'name': fields.String,
    'balance': fields.Float(attribute=lambda x: x.get_balance())
}

class AccountListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(account_fields)
    def get(self) -> List[Account]:
        return list(Account.objects(owner=auth.current_user()))

    @marshal_with(account_fields)
    def post(self) -> Account:
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        args = parser.parse_args()

        account = Account(name=args['name'], owner=auth.current_user())
        account.save()
        return account