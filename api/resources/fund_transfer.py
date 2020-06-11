
import datetime
from flask_restful import Resource, reqparse, marshal_with
from decimal import Decimal

from api.authentication import auth
from models.fund_transfer_transaction import FundTransferTransaction

from api.resources.transaction_list import transaction_fields

from bson.objectid import ObjectId

class FundTransferResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(transaction_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('from', type=ObjectId, required=True)
        parser.add_argument('to', type=ObjectId, required=True)
        parser.add_argument('amount', type=Decimal, required=True)
        args = parser.parse_args()

        transaction = FundTransferTransaction(owner=auth.current_user(), from_fund_id=args['from'], to_fund_id=args['to'],
                                                 amount=args['amount'],
                                                 time_accomplished=datetime.datetime.now())
        transaction.save()

        return transaction