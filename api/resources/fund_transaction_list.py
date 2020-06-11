
from flask_restful import Resource
from api.authentication import auth

class FundTranasctionList(Resource):
    method_decorators = [auth.login_required]

    def get(self, fund_id: str):
        pass

