
from flask import request
from mongoengine import ValidationError
import flask
from flask_restful import fields, Resource, reqparse, marshal_with
from models.transaction import Transaction
from models.income_transaction import IncomeTransaction
from models.expense_transaction import ExpenseTransaction
from api.authentication import auth
import dateutil.parser
from ..pagination import paged_entity_scheme, create_page_response

account_transaction_fields = {
    'account': fields.String(attribute='account.id'),
    'change': fields.Float
}

fund_transaction_fields = {
    'fund': fields.String(attribute='fund.id'),
    'change': fields.Float
}

transaction_fields = {
    'id': fields.String,
    'description': fields.String,
    'category': fields.String(attribute='category.id'),
    'date_accomplished': fields.DateTime(dt_format='iso8601'),
    'account_transactions': fields.List(fields.Nested(account_transaction_fields)),
    'fund_transactions': fields.List(fields.Nested(fund_transaction_fields))
}



class TransactionListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(transaction_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('description')
        parser.add_argument('account_id', type=str, required=True)
        parser.add_argument('change', type=float, required=True) # TODO: Add validation, must be different from 0
        parser.add_argument('category')
        parser.add_argument('date_accomplished', type=lambda t: dateutil.parser.parse(t))
        args = parser.parse_args()

        if args['change'] == 0:
            flask.abort(400, "Change must be different from zero")


        if args['change'] > 0:

            transaction = IncomeTransaction(account_id=args['account_id'],
                                                    change=args['change'],
                                                    description=args['description'],
                                                    category=args['category'],
                                                    date_accomplished=args['date_accomplished'],
                                                    owner=auth.current_user())

        if args['change'] < 0:
            transaction = ExpenseTransaction(account_id=args['account_id'],
                                            change=args['change'],
                                            description=args['description'],
                                            category=args['category'],
                                            date_accomplished=args['date_accomplished'],
                                            owner=auth.current_user())

        try:
            transaction.save()
        except ValidationError as ex:
            flask.abort(400, ex.message)

        args['date_accomplished'] = str(args['date_accomplished'])
        return transaction


    @marshal_with(paged_entity_scheme(transaction_fields))
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('account_id', type=str, store_missing=False)
        parser.add_argument('fund_id', type=str, store_missing=False)
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('page_size', type=int, default=30)
        args = parser.parse_args()

        match = {'owner': auth.current_user()}

        if 'account_id' in args:
            match['account_transactions__account'] = args['account_id']

        if 'fund_id' in args:
            match['fund_transactions__fund'] = args['fund_id']

        query = Transaction.objects(**match).order_by('-date_accomplished')

        return create_page_response(query)