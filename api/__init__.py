from flask import Flask, Blueprint
from flask_restful import Api
from api.resources.account_list import AccountListResource
from api.resources.category_list import CategoriesList
from api.resources.subcategory_list import SubcategoriesList
from api.resources.account_transaction_list import AccountTransactionListResource
from api.resources.account_transaction_transfer import AccountTransactionTransfer
from api.resources.account_transaction import AccountTransactionResource
from api.resources.fund_list import FundListResource
from api.resources.fund_transfer import FundTransferResource

from .authentication import auth

bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(bp)

resources = (
    #('/categories/<string:category_id>/subcategories', SubcategoriesList),
    ('/funds', FundListResource),
    ('/funds/<string:fund_id>/categories', CategoriesList),
    ('/accounts', AccountListResource),
    ('/account/<string:account_id>/transactions', AccountTransactionListResource),
    ('/account/<string:account_id>/transaction/<string:transaction_id>', AccountTransactionResource),
    ('/account/<string:account_id>/transfer', AccountTransactionTransfer),
    ('/fund/<string:fund_id>/transfer', FundTransferResource)
)

for resource in resources:
    api.add_resource(resource[1], resource[0])


