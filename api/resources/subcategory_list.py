
from flask import request
from flask_restful import fields, Resource, marshal_with

from api.authentication import auth
from models.category import TransactionCategory

subcategory_fields = {
    'id': fields.String,
    'name': fields.String,
    'parent': fields.String(attribute='parent.id')
}

class SubcategoriesList(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(subcategory_fields)
    def get(self, category_id):
        query = TransactionCategory.objects(parent=category_id, owner=auth.current_user())
        return list(query)

    @marshal_with(subcategory_fields)
    def post(self, category_id):
        category = TransactionCategory(name=request.form['name'], owner=auth.current_user(), parent=category_id)
        category.save()
        return category
