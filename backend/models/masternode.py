from datetime import datetime, timedelta
from .base import db
from pony import orm

class Masternode(db.Entity):
    _table_ = "chain_masternodes"

    created = orm.Required(datetime, default=datetime.utcnow)
    active = orm.Required(bool, default=False)
    rank = orm.Optional(int, nullable=True)
    activetime = orm.Required(timedelta)
    lastseen = orm.Required(datetime)
    lastpaid = orm.Required(datetime)
    address = orm.Required("Address")
    version = orm.Required(int)
    txhash = orm.Required(str)
    outidx = orm.Required(int)
    status = orm.Required(str)
    pubkey = orm.Required(str)
