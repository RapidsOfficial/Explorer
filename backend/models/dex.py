from datetime import datetime

from backend.utils import amount
from .base import db
from pony import orm

class DexOffer(db.Entity):
    _table_ = "chain_dex_offers"

    feerequired = orm.Required(float, default=0)
    open = orm.Required(bool, default=True)
    filled = orm.Required(float, default=0)
    amount = orm.Required(float, default=0)
    price = orm.Required(float, default=0)
    address = orm.Required("Address")
    created = orm.Required(datetime)
    timelimit = orm.Required(int)
    currency = orm.Required(str)

    purchases = orm.Set("DexPurchase")

class DexPurchase(db.Entity):
    _table_ = "chain_dex_purchases"

    amount = orm.Required(float, default=0)
    address = orm.Required("Address")
    created = orm.Required(datetime)
    offer = orm.Required("DexOffer")
