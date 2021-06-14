from datetime import datetime
from .base import db
from pony import orm

class Peer(db.Entity):
    _table_ = "chain_peers"

    created = orm.Required(datetime, default=datetime.utcnow)
    active = orm.Required(bool, default=False)
    version = orm.Required(int)
    address = orm.Required(str)
    subver = orm.Required(str)
    port = orm.Required(int)

    location = orm.Optional("Location")

class Location(db.Entity):
    _table_ = "chain_peer_location"

    country = orm.Required(str)
    peer = orm.Required("Peer")
    lat = orm.Required(float)
    lon = orm.Required(float)
    city = orm.Required(str)
    code = orm.Required(str)
