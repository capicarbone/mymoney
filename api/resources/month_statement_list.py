
from collections import namedtuple
from api.authentication import auth
from flask_restful import Resource, marshal_with, reqparse, fields
from models.month_statement import MonthStatement

month_statement_fields = {
    '_id': fields.String(attribute='id'),
    'month': fields.Integer,
    'year': fields.Integer
}

page = {
    '_items': fields.List(fields.Nested(month_statement_fields), attribute='items'),
    '_count': fields.Integer(attribute='count'),
    '_page': fields.Integer(attribute='page')
}

class MonthStatementListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(page)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('year', type=int, store_missing=False)
        parser.add_argument('month', type=int, store_missing=False)
        query_args = parser.parse_args()
        query_args['owner'] = auth.current_user()

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=0)
        parser.add_argument('items_per_page', type=int, default=12)
        pagination_args = parser.parse_args()
        items_per_page = pagination_args['items_per_page']
        page = pagination_args['page']

        statements = MonthStatement.objects(**query_args)\
            .order_by('-year', '-month')\
            .limit(items_per_page)\
            .skip(page*items_per_page)

        Page = namedtuple('Page', ['items', 'count', 'page'])

        return Page(
            items=statements.all(),
            count=statements.count(),
            page=page
        )._asdict()


