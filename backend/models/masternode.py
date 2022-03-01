from datetime import datetime
from .base import db
from pony import orm

class Masternode(db.Entity):
    _table_ = "chain_masternodes"

    created = orm.Required(datetime, default=datetime.utcnow)
    active = orm.Required(bool, default=False)
    rank = orm.Optional(int, nullable=True)
    lastseen = orm.Required(datetime)
    lastpaid = orm.Required(datetime)
    activetime = orm.Required(int)
    address = orm.Required(str)
    version = orm.Required(int)
    txhash = orm.Required(str)
    outidx = orm.Required(int)
    status = orm.Required(str)
    pubkey = orm.Required(str)

    @property
    def display(self):
        return {
            "lastseen": int(self.lastseen.timestamp()),
            "lastpaid": int(self.lastpaid.timestamp()),
            "created": int(self.created.timestamp()),
            "activetime": self.activetime,
            "version": self.version,
            "address": self.address,
            "txhash": self.txhash,
            "outidx": self.outidx,
            "status": self.status,
            "pubkey": self.pubkey,
            "active": self.active,
            "rank": self.rank
        }
