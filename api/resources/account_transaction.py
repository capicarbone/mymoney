
import flask
from decimal import Decimal
from flask_restful import Resource, marshal_with, reqparse
from models.transaction import Transaction
from api.authentication import auth
from api.resources.transaction_list import transaction_fields
import dateutil.parser
from bson.objectid import ObjectId

class AccountTransactionResource(Resource):

    method_decorators = [auth.login_required]

    @marshal_with(transaction_fields)
    def put(self, account_id, transaction_id):
        parser = reqparse.RequestParser()
        parser.add_argument('description', store_missing=False)
        #parser.add_argument('account', type=ObjectId, store_missing=False)
        parser.add_argument('category', type=ObjectId, store_missing=False)
        parser.add_argument('time_accomplished', store_missing=False, type=lambda t: dateutil.parser.parse(t))
        entity_args = parser.parse_args()

        parser = reqparse.RequestParser()
        parser.add_argument('change', type=Decimal, store_missing=False)  # TODO: Add validation, must be different from 0
        change_arg = parser.parse_args()

        if len(entity_args) > 0:
            Transaction.objects(owner=auth.current_user(), id=transaction_id).update(**entity_args)

        if len(change_arg) > 0:
            transaction = Transaction.objects(owner=auth.current_user(), id=transaction_id).get()
            transaction.adjust_change(change_arg['change'])



        transaction = Transaction.objects(owner=auth.current_user(), id=transaction_id).get()

        return transaction

    def delete(self, account_id, transaction_id):

        t = Transaction.objects(id=transaction_id, owner=auth.current_user())
        t.delete()

        return "", 204