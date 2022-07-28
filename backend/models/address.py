from datetime import datetime
from .base import db
from pony import orm

class Address(db.Entity):
    _table_ = "chain_addresses"

    # ToDo: POS info?

    address = orm.Required(str, index=True)
    lastactive = orm.Required(datetime)
    created = orm.Required(datetime)

    transactions = orm.Set(
        "Transaction", table="chain_address_transactions",
        reverse="addresses"
    )

    # trades_received = orm.Set("Trade", reverse="receiver")
    # trades_sent = orm.Set("Trade", reverse="sender")

    balances = orm.Set("Balance")
    outputs = orm.Set("Output")
    issued = orm.Set("Token")

    dex_purchases = orm.Set("DexPurchase")
    dex_offers = orm.Set("DexOffer")
    orders = orm.Set("TradeOrder")

    received = orm.Set("Transfer")
    sent = orm.Set("Transfer")

    @property
    def txcount(self):
        return self.transactions.count()

    @property
    def txs(self):
        transactions = self.transactions.order_by(-1)
        return transactions
