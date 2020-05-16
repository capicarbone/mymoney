
from flask import abort
import mongoengine
from api.resources.category_list import category_fields
from flask_restful import Resource, fields, marshal_with, reqparse
from models.fund import Fund
from api.authentication import auth

fund_fields = {
    'id' : fields.String,
    'name': fields.String,
    'description': fields.String,
    'minimum_limit': fields.Float,
    'maximum_limit': fields.Float,
    'percentage_assigment': fields.Float,
    'balance': fields.Float(attribute=lambda x: x.get_balance()),
    'categories': fields.List(fields.Nested(category_fields))

}

class FundListResource(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(fund_fields)
    def get(self):
        funds = Fund.objects(owner=auth.current_user())
        return list(funds)

    @marshal_with(fund_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('description')
        parser.add_argument('minimum_limit', type=float)
        parser.add_argument('maximum_limit', type=float)
        parser.add_argument('percentage_assigment', type=float, required=True)
        args = parser.parse_args()

        fund = Fund(**args)
        fund.owner = auth.current_user()

        try:
            fund.save()
        except mongoengine.ValidationError as ex:
            abort(400, str(ex.errors['__all__']))

        return fund


