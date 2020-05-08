
import mongoengine
from flask import abort
from models.category import FundCategory
from models.fund import Fund

from api.authentication import auth
from api.resources.subcategory_list import subcategory_fields
from flask_restful import Resource, marshal_with, reqparse, fields

category_fields = {
    'id': fields.String,
    'name': fields.String,
}

class CategoriesList(Resource):
    method_decorators = [auth.login_required]

    def __get_fund(self, fund_id):
        try:
            return Fund.objects(id=fund_id, owner=auth.current_user()).get()
        except mongoengine.DoesNotExist:
            abort(404)

    @marshal_with(category_fields)
    def get(self, fund_id):
        fund = self.__get_fund(fund_id)
        return list(fund.categories)

    @marshal_with(category_fields)
    def post(self, fund_id):
        self.__get_fund(fund_id)

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        args = parser.parse_args()

        category = FundCategory(name=args['name'], owner=auth.current_user())
        category.save()

        Fund.objects(id=fund_id).update_one(add_to_set__categories=category)

        return category