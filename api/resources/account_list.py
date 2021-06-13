
from typing import List
from flask_restful import Resource, marshal_with, fields, reqparse
from api.authentication import auth
from models import InitialBalanceTransaction, Account
from flask import abort

account_fields = {
    'id': fields.String,
    'name': fields.String,
    'balance': fields.Float(attribute=lambda x: x.balance)
}

class AccountListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(account_fields)
    def get(self) -> List[Account]:
        return list(Account.objects(owner=auth.current_user()))

    @marshal_with(account_fields)
    def post(self) -> Account:
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, type=str)
        parser.add_argument('initial_balance', type=float, store_missing=False)
        args = parser.parse_args()

        if not args['name']:
            abort(400, description="Name can't be blank")

        account = Account(name=args['name'], owner=auth.current_user())
        account.save()

        if 'initial_balance' in args:
            InitialBalanceTransaction(
                owner=auth.current_user(),
                account_id=account.id,
                change=args['initial_balance']
            ).save()

        return account