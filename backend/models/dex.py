from datetime import datetime
from .base import db
from pony import orm

class DexOffer(db.Entity):
    _table_ = "chain_dex_offers"

    feerequired = orm.Required(float, default=0)
    transaction = orm.Required("Transaction")
    open = orm.Required(bool, default=True)
    filled = orm.Required(float, default=0)
    amount = orm.Required(float, default=0)
    price = orm.Required(float, default=0)
    address = orm.Required("Address")
    created = orm.Required(datetime)
    timelimit = orm.Required(int)
    currency = orm.Required(str)

    purchases = orm.Set("DexPurchase")

    @property
    def display(self):
        purchases = []

        for purchase in self.purchases:
            purchases.append(purchase.display)

        return {
            "created": int(self.created.timestamp()),
            "transaction": self.transaction.txid,
            "feerequired": self.feerequired,
            "address": self.address.address,
            "timelimit": self.timelimit,
            "currency": self.currency,
            "purchases": purchases,
            "filled": self.filled,
            "amount": self.amount,
            "price": self.price,
            "open": self.open
        }

class DexPurchase(db.Entity):
    _table_ = "chain_dex_purchases"

    transaction = orm.Required("Transaction")
    amount = orm.Required(float, default=0)
    address = orm.Required("Address")
    created = orm.Required(datetime)
    offer = orm.Required("DexOffer")

    @property
    def display(self):
        return {
            "created": int(self.created.timestamp()),
            "transaction": self.transaction.txid,
            "address": self.address.address,
            "amount": self.amount,
        }
