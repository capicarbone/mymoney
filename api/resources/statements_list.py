
from collections import namedtuple
from api.authentication import auth
from flask_restful import Resource, marshal_with, reqparse, fields
from models.statement import Statement, AccountChange
from ..pagination import paged_entity_scheme, Page, create_page_response

account_change = {
    'account_id': fields.String(attribute='account.id'),
    'expense': fields.Float,
    'income': fields.Float
}

fund_change = {
    'fund_id': fields.String(attribute='fund.id'),
    'expense': fields.Float,
    'income': fields.Float
}

category_change = {
    'category_id': fields.String(attribute='category.id'),
    'change': fields.Float
}

month_statement_fields = {
    '_id': fields.String(attribute='id'),
    'level': fields.Integer,
    'month': fields.Integer,
    'year': fields.Integer,
    'accounts': fields.List(fields.Nested(account_change)),
    'funds': fields.List(fields.Nested(fund_change)),
    'categories': fields.List(fields.Nested(category_change))
}


class StatementListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(paged_entity_scheme(month_statement_fields))
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('year', type=int, store_missing=False)
        parser.add_argument('month', type=int, store_missing=False)
        query_args = parser.parse_args()
        query_args['owner'] = auth.current_user()

        query = Statement.objects(**query_args)\
            .order_by('level', '-year', '-month')

        return create_page_response(query)


