
from flask import request
from models.category import TransactionCategory, CATEGORY_TYPES

from api.authentication import auth
from api.resources.subcategory_list import subcategory_fields
from flask_restful import Resource, marshal_with, reqparse, fields

category_fields = {
    'id': fields.String,
    'name': fields.String,
    'type': fields.String,
    'subcategories': fields.List(fields.Nested(subcategory_fields), attribute=lambda c: list(c.get_subcategories()))
}

class CategoriesList(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(category_fields)
    def get(self):
        query = {
            'parent': None,
            'owner': auth.current_user()
        }

        cat_type  = request.args.get('type', None)

        if cat_type in CATEGORY_TYPES:
            query['type'] = cat_type

        return list(TransactionCategory.objects(**query))

    @marshal_with(category_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('type', required=True, choices=CATEGORY_TYPES)
        args = parser.parse_args()

        category = TransactionCategory(name=args['name'], type=args['type'], owner=auth.current_user(), parent=None)
        category.save()
        return category