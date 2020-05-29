
import flask
import mongoengine
from flask_restful import Resource, reqparse
from api.authentication import auth
import dateutil.parser
from decimal import Decimal
from models.transaction import Transaction

class AccountTransactionTransfer(Resource):
    method_decorators = [auth.login_required]

    def post(self, account_id):
        parser = reqparse.RequestParser()
        parser.add_argument('to', type=str, required=True)
        parser.add_argument('amount', type=Decimal, required=True)
        parser.add_argument('description', type=str)
        parser.add_argument('time_accomplished', type=lambda t: dateutil.parser.parse(t))
        args = parser.parse_args()

        transaction = Transaction.create_account_transfer(auth.current_user(), account_id, args['to'], args['amount'],
                                                          description=args['description'],
                                                          time_accomplished=args['time_accomplished'])
        transaction.save()

        return {'id': str(transaction.id)}