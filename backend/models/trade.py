from datetime import datetime
from .base import db
from pony import orm

class TradeOrder(db.Entity):
    _table_ = "chain_trade_orders"

    amountforsale = orm.Required(float, default=0)
    amountdesired = orm.Required(float, default=0)
    open = orm.Required(bool, default=True)
    filled = orm.Required(float, default=0)
    currencyforsale = orm.Required(str)
    currencydesired = orm.Required(str)
    address = orm.Required("Address")
    created = orm.Required(datetime)
    txid = orm.Required(str)

    transaction = orm.Required("Transaction")

    matches_sell = orm.Set("TradeMatch", reverse="order_seller")
    matches_buy = orm.Set("TradeMatch", reverse="order_buyer")

    @property
    def price(self):
        return round(self.amountforsale / self.amountdesired, 8)

    @property
    def display(self):
        sell = [m.display for m in self.matches_sell]
        buy = [m.display for m in self.matches_buy]

        return {
            "created": int(self.created.timestamp()),
            "currencyforsale": self.currencyforsale,
            "currencydesired": self.currencydesired,
            "transaction": self.transaction.txid,
            "amountforsale": self.amountforsale,
            "amountdesired": self.amountdesired,
            "address": self.address.address,
            "filled": self.filled,
            "price": self.price,
            "open": self.open,
            "sell": sell,
            "buy": buy
        }

class TradeMatch(db.Entity):
    _table_ = "chain_trade_matches"

    amountreceived = orm.Required(float, default=0)
    amountsold = orm.Required(float, default=0)

    order_seller = orm.Required("TradeOrder")
    order_buyer = orm.Required("TradeOrder")
    created = orm.Required(datetime)

    @property
    def display(self):
        return {
            "order_seller": self.order_seller.transaction.txid,
            "order_buyer": self.order_buyer.transaction.txid,
            "created": int(self.created.timestamp()),
            "amountreceived": self.amountreceived,
            "amountsold": self.amountsold
        }


