
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
    '_count': fields.Integer(attribute='count')
}

class MonthStatementListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(page)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('year', type=int)
        parser.add_argument('month', type=int)
        args = parser.parse_args()

        args['owner'] = auth.current_user()
        statements = MonthStatement.objects(**args).order_by('-year', '-month')

        Page = namedtuple('Page', ['items', 'count'])

        return Page(
            items=statements.all(),
            count=statements.count()
        )._asdict()


