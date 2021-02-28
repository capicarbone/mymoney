
import pytest
import mongoengine
from flask import abort, request
from models.category import TransactionCategory
from models.fund import Fund

from api.authentication import auth
from api.resources.subcategory_list import subcategory_fields
from flask_restful import Resource, marshal_with, reqparse, fields

category_fields = {
    'id': fields.String,
    'name': fields.String,
    'kind': fields.String
}

class CategoriesList(Resource):
    method_decorators = [auth.login_required]

    def __is_fund_required(self):
        if request.form:
            return request.form['kind'] == 'expense'

        if request.json:
            return request.json['kind'] == 'expense'

        return False

    def __get_fund(self, fund_id):
        try:
            return Fund.objects(id=fund_id, owner=auth.current_user()).get()
        except mongoengine.DoesNotExist:
            abort(404)

    @marshal_with(category_fields)
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('fund_id', type=str, store_missing=False)
        args = parser.parse_args()

        if 'fund_id' in args:
            fund = self.__get_fund(args['fund_id'])
            return list(fund.categories)

        user_categories = TransactionCategory.objects(owner=auth.current_user()).all()
        return list(user_categories)

    @marshal_with(category_fields)
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('kind', required=True, choices=['income', 'expense'])
        parser.add_argument('fund', required=self.__is_fund_required())
        args = parser.parse_args()

        category = TransactionCategory(name=args['name'],
                                       kind=args['kind'],
                                       owner=auth.current_user())

        category.save()

        if not category.is_income():
            Fund.objects(id=args['fund'], owner=auth.current_user())\
                .update_one(add_to_set__categories=category)

        return category