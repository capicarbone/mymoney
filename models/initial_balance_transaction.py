from decimal import Decimal

import mongoengine
from mongoengine import signals

from .fund import Fund
from .transaction import Transaction, AccountTransaction, FundTransaction

class InitialBalanceTransaction(Transaction):

    def __init__(self, **kwargs):

        parameters = self._extract_utilitaries_paramenters(kwargs)

        change: Decimal = parameters[0]
        account_id: str = parameters[1]

        super().__init__(**kwargs)

        if change and account_id:
            account_transaction = AccountTransaction(account=account_id, change=change)
            self.account_transactions.append(account_transaction)
        else:
            raise Exception('change and account_id required for initialization')

    def clean(self):
        super().clean()

        if len(self.fund_transactions) != 1 or len(self.account_transactions) != 1:
            raise mongoengine.ValidationError("Fund or account transacion missing")

    def __add_fund_transaction(self):
        """
        Creates fund transaction iff necessary
        :return:
        """
        #import pytest; pytest.set_trace()
        if len(self.fund_transactions) == 0:
            default_fund = Fund.objects(owner=self.owner, is_default=True).get()
            fund_transaction = FundTransaction(fund=default_fund, change=self.total_change)
            self.fund_transactions.append(fund_transaction)

    @classmethod
    def pre_save_post_validation(cls, sender, document: 'InitialBalanceTransaction'):
        document.__add_fund_transaction()


signals.pre_save.connect(InitialBalanceTransaction.pre_save_post_validation,
                                         sender=InitialBalanceTransaction)
