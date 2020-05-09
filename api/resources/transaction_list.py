
from flask import request
from flask_restful import fields, Resource, reqparse, marshal_with
from models.transaction import AccountTransaction
from api.authentication import auth
import dateutil.parser

from flask_mongoengine import MongoEngine

transaction_fields = {
    'id': fields.String,
    'description': fields.String,
    'account': fields.String(attribute='account.id'),
    'change': fields.Float,
    'category': fields.String(attribute='category.id'),
    'time_accomplished': fields.DateTime(dt_format='iso8601')
}



class TransactionListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(transaction_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('description')
        parser.add_argument('change', type=float, required=True)
        parser.add_argument('category', required=True)
        parser.add_argument('account', required=True)
        parser.add_argument('time_accomplished', type=lambda t: dateutil.parser.parse(t))
        args = parser.parse_args()

        args['owner'] = auth.current_user()
        transaction = AccountTransaction(**args)
        transaction.save()

        return transaction

    @marshal_with(transaction_fields)
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('page_size', type=int, default=30)
        parser.add_argument('account', default=None)
        args = parser.parse_args()

        query = {}
        if args['account']:
            query['account'] = args['account']

        return AccountTransaction.objects(**query).paginate(page=args['page'], per_page=args['page_size']).items