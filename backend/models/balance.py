from ..constants import CURRENCY
from .base import db
from pony import orm

class Balance(db.Entity):
    _table_ = "chain_address_balance"

    balance = orm.Required(float, default=0)
    received = orm.Required(float, default=0)
    sent = orm.Required(float, default=0)
    address = orm.Required("Address")
    currency = orm.Required(str)

    orm.composite_index(address, currency)

class Input(db.Entity):
    _table_ = "chain_inputs"

    sequence = orm.Required(int, size=64)
    n = orm.Required(int)

    transaction = orm.Required("Transaction")
    vout = orm.Required("Output", index=True)

    def before_delete(self):
        balance = Balance.get(
            address=self.vout.address, currency=self.vout.currency
        )

        balance.balance += self.vout.amount
        balance.sent -= self.vout.amount

class Output(db.Entity):
    _table_ = "chain_outputs"

    amount = orm.Required(float)
    currency = orm.Required(str, default=CURRENCY, index=True)
    address = orm.Required("Address")
    category = orm.Optional(str)
    raw = orm.Optional(str)
    n = orm.Required(int)

    vin = orm.Optional("Input", cascade_delete=True)
    transaction = orm.Required("Transaction")
    address = orm.Optional("Address")

    @property
    def spent(self):
        return self.vin is not None

    def before_delete(self):
        balance = Balance.get(
            address=self.address, currency=self.currency
        )

        balance.balance -= self.amount
        balance.received -= self.amount

    orm.composite_index(transaction, n)
