
from flask import request
from mongoengine import ValidationError
import flask
from flask_restful import fields, Resource, reqparse, marshal_with
from models.transaction import Transaction
from models.income_transaction import IncomeTransaction
from models.expense_transaction import ExpenseTransaction
from api.authentication import auth
import dateutil.parser

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
    'time_accomplished': fields.DateTime(dt_format='iso8601'),
    'account_transactions': fields.List(fields.Nested(account_transaction_fields)),
    'fund_transactions': fields.List(fields.Nested(fund_transaction_fields))
}



class AccountTransactionListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(transaction_fields)
    def post(self, account_id: str):
        parser = reqparse.RequestParser()
        parser.add_argument('description')
        parser.add_argument('change', type=float, required=True) # TODO: Add validation, must be different from 0
        parser.add_argument('category')
        parser.add_argument('time_accomplished', type=lambda t: dateutil.parser.parse(t))
        args = parser.parse_args()

        if args['change'] == 0:
            flask.abort(400, "Change must be different from zero")


        if args['change'] > 0:

            transaction = IncomeTransaction(account_id=account_id,
                                                    change=args['change'],
                                                    description=args['description'],
                                                    time_accomplished=args['time_accomplished'],
                                                    owner=auth.current_user())

        if args['change'] < 0:
            transaction = ExpenseTransaction(account_id=account_id,
                                            change=args['change'],
                                            description=args['description'],
                                            category=args['category'],
                                            time_accomplished=args['time_accomplished'],
                                            owner=auth.current_user())

        try:
            transaction.save()
        except ValidationError as ex:
            flask.abort(400, ex.message)

        args['time_accomplished'] = str(args['time_accomplished'])
        return transaction


    @marshal_with(transaction_fields)
    def get(self, account_id:str):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('page_size', type=int, default=30)
        args = parser.parse_args()

        return Transaction.objects(account_transactions__account=account_id).paginate(page=args['page'], per_page=args['page_size']).items