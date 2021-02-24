
from flask_restful import Resource, reqparse, marshal_with
from api.authentication import auth
import dateutil.parser
from decimal import Decimal
from models.accounts_transfer_transaction import AccountsTransferTransaction

from api.resources.transaction_list import transaction_fields

from bson.objectid import ObjectId

# TODO: Rename to AccountTransfer
class AccountTransactionTransfer(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(transaction_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('from', type=ObjectId, required=True)
        parser.add_argument('to', type=ObjectId, required=True)
        parser.add_argument('amount', type=Decimal, required=True)
        parser.add_argument('description', type=str)
        parser.add_argument('date_accomplished',
                            type=lambda t: dateutil.parser.parse(t),
                            required=True
                            )
        args = parser.parse_args()

        transaction = AccountsTransferTransaction(owner=auth.current_user(), from_account_id=args['from'], to_account_id=args['to'],
                                                 amount=args['amount'],
                                                 description=args['description'],
                                                 date_accomplished=args['date_accomplished'])
        transaction.save()

        return transaction