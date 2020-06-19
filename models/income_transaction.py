
import mongoengine
from decimal import Decimal
from models.account_transaction import AccountTransaction
from models.transaction import Transaction
from models.fund import Fund
from utils import fund_utils
from mongoengine import signals

class IncomeTransaction(Transaction):

    def __init__(self, **kwargs):

        change:Decimal = kwargs.pop('change') if 'change' in kwargs else None
        account_id:str = kwargs.pop('account_id') if 'account_id' in kwargs else None

        super().__init__(**kwargs)

        if change and account_id:

            if change <= 0:
                raise mongoengine.ValidationError("Change must be positive for an income")


            account_transaction = AccountTransaction(account=account_id, change=change)
            self.account_transactions.append(account_transaction)

    def __proccess_income(self):

        funds = Fund.objects().actives_for(self.owner)
        assignments = fund_utils.create_assignments_for_income(funds, self.total_change, self.time_accomplished)
        self.fund_transactions = assignments

    def adjust_change(self, change):

        super().adjust_change(change)

        if change <= 0:
            raise mongoengine.ValidationError("Change invalid.")

        funds_to_adjust = [t.fund.fetch() for t in self.fund_transactions]

        new_account_transaction = self.account_transactions[0]
        new_account_transaction.change = Decimal(change).quantize(Decimal("1.00"))

        new_fund_transactions = fund_utils.create_assignments_for_income(funds_to_adjust, self.total_change, self.time_accomplished, self.id)

        # TODO: I should add adjustments for funds that are currently above their max limit and those removed fund above 0

        self.update(account_transactions=[new_account_transaction], fund_transactions=new_fund_transactions)

    @classmethod
    def pre_save_post_validation(cls, sender, document: 'IncomeTransaction', created):
        document.__proccess_income()

        assert sum([ft.change for ft in document.fund_transactions]) == document.total_change


signals.pre_save_post_validation.connect(IncomeTransaction.pre_save_post_validation, sender=IncomeTransaction)



