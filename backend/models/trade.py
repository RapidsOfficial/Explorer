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
    txid = orm.Required(str)

    transaction = orm.Required("Transaction")

    matches_sell = orm.Set("TradeMatch", reverse="order_seller")
    matches_buy = orm.Set("TradeMatch", reverse="order_buyer")

class TradeMatch(db.Entity):
    _table_ = "chain_trade_matches"

    amountreceived = orm.Required(float, default=0)
    amountsold = orm.Required(float, default=0)

    order_seller = orm.Required("TradeOrder")
    order_buyer = orm.Required("TradeOrder")


