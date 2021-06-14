# from ..constants import REDUCTION_HEIGHT, DECIMALS
from datetime import datetime
from .base import db
from pony import orm

class Reward(db.Entity):
    _table_ = "chain_block_rewards"

    reward = orm.Required(float, default=0)
    dev = orm.Required(float, default=0)
    mn = orm.Required(float, default=0)

    block = orm.Required("Block")

class Block(db.Entity):
    _table_ = "chain_blocks"

    blockhash = orm.Required(str, index=True)
    height = orm.Required(int, size=64, index=True)
    bits = orm.Required(int, size=64)
    created = orm.Required(datetime)
    merkleroot = orm.Required(str)
    version = orm.Required(int)
    stake = orm.Required(bool)
    nonce = orm.Required(int)
    size = orm.Required(int)

    previous_block = orm.Optional("Block")
    transactions = orm.Set("Transaction")
    next_block = orm.Optional("Block")
    reward = orm.Optional("Reward")

    @property
    def txs(self):
        transactions = self.transactions.order_by(1)
        return transactions

    @property
    def timestamp(self):
        return int(self.created.timestamp())

    @property
    def txcount(self):
        return self.transactions.count()

    @property
    def confirmations(self):
        latest_blocks = Block.select().order_by(
            orm.desc(Block.height)
        ).first()

        return latest_blocks.height - self.height + 1
