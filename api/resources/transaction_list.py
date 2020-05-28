
from flask import request
from mongoengine import ValidationError
import flask
from flask_restful import fields, Resource, reqparse, marshal_with
from models.transaction import Transaction
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

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('description')
        parser.add_argument('change', type=float, required=True)
        parser.add_argument('category')
        parser.add_argument('account', required=True)
        parser.add_argument('time_accomplished', type=lambda t: dateutil.parser.parse(t))
        args = parser.parse_args()


        if args['change'] > 0:
            transaction = Transaction.create_income(args['account'],
                                                    args['change'],
                                                    args['description'],
                                                    args['time_accomplished'],
                                                    auth.current_user())

        try:
            transaction.save()
        except ValidationError as ex:
            flask.abort(400, ex.message)

        args['time_accomplished'] = str(args['time_accomplished'])
        return args


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

        return Transaction.objects(**query).paginate(page=args['page'], per_page=args['page_size']).items