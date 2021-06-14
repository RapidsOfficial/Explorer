from .base import db
from pony import orm

class Stats(db.Entity):
    _table_ = "chain_stats"

    value = orm.Required(float, default=0)
    key = orm.Required(str, index=True)
