from flask import Flask, Blueprint
from flask_restful import Api
from api.resources.account_list import AccountListResource
from api.resources.category_list import CategoriesList
from api.resources.subcategory_list import SubcategoriesList
from api.resources.transaction_list import TransactionListResource
from api.resources.fund_list import FundListResource

from .authentication import auth

bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(bp)

resources = (
    #('/categories/<string:category_id>/subcategories', SubcategoriesList),
    ('/funds', FundListResource),
    ('/funds/<string:fund_id>/categories', CategoriesList),
    ('/accounts', AccountListResource),
    ('/transactions', TransactionListResource)
)

for resource in resources:
    api.add_resource(resource[1], resource[0])


