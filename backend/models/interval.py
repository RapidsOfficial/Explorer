from datetime import datetime
from .base import db
from pony import orm

class Interval(db.Entity):
    _table_ = "chain_invervals"

    value = orm.Required(int, default=0)
    key = orm.Required(str, index=True)
    time = orm.Required(datetime)
