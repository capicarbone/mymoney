
from flask import request
from mongoengine import ValidationError
import flask
from flask_restful import fields, Resource, reqparse, marshal_with
from models.transaction import Transaction
from api.authentication import auth
import dateutil.parser

transaction_fields = {
    'id': fields.String,
    'description': fields.String,
    'account': fields.String(attribute='account.id'),
    'change': fields.Float,
    'category': fields.String(attribute='category.id'),
    'time_accomplished': fields.DateTime(dt_format='iso8601')
}



class AccountTransactionListResource(Resource):
    method_decorators = [auth.login_required]

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
            transaction = Transaction.create_income(account_id,
                                                    args['change'],
                                                    args['description'],
                                                    args['time_accomplished'],
                                                    auth.current_user())

        if args['change'] < 0:
            transaction = Transaction.create_expense(account_id,
                                                    args['change'],
                                                    args['description'],
                                                    args['time_accomplished'],
                                                    args['category'],
                                                    auth.current_user())

        try:
            transaction.save()
        except ValidationError as ex:
            flask.abort(400, ex.message)

        args['time_accomplished'] = str(args['time_accomplished'])
        return args


    @marshal_with(transaction_fields)
    def get(self, account_id:str):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('page_size', type=int, default=30)
        args = parser.parse_args()

        return Transaction.objects(account=account_id).paginate(page=args['page'], per_page=args['page_size']).items