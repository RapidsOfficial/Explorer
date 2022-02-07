from .base import db
from pony import orm

class Token(db.Entity):
    _table_ = "chain_tokens"

    subcategory = orm.Optional(str, nullable=True)
    category = orm.Optional(str, nullable=True)
    data = orm.Optional(str, nullable=True)
    url = orm.Optional(str, nullable=True)
    supply = orm.Required(float, default=0)
    name = orm.Required(str, index=True)
    divisible = orm.Required(bool)
    crowdsale = orm.Required(bool)
    managed = orm.Required(bool)

    transaction = orm.Required("Transaction")
    issuer = orm.Required("Address")
    transfers = orm.Set("Transfer")

class Transfer(db.Entity):
    _table_ = "chain_transfers"

    transaction = orm.Required("Transaction")
    crowdsale = orm.Required(bool, default=False)
    create = orm.Required(bool, default=False)
    burn = orm.Required(bool, default=False)
    amount = orm.Required(float, default=0)

    receiver = orm.Optional("Address", reverse="received")
    sender = orm.Optional("Address", reverse="sent")
    token = orm.Required("Token")
