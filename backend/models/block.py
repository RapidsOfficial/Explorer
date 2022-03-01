from ..constants import DECIMALS
from datetime import datetime
from .base import db
from pony import orm
from .. import utils

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

    reward = orm.Required(float, default=0)
    dev = orm.Required(float, default=0)
    mn = orm.Required(float, default=0)

    previous_block = orm.Optional("Block")
    transactions = orm.Set("Transaction")
    next_block = orm.Optional("Block")

    @property
    def display(self):
        return {
            "reward": utils.round_amount(self.reward),
            "blockhash": self.blockhash,
            "height": self.height,
            "tx": len(self.transactions),
            "timestamp": int(self.created.timestamp()),
            "merkleroot": self.merkleroot,
            "version": self.version,
            "stake": self.stake,
            "nonce": self.nonce,
            "size": self.size,
            "bits": self.bits
        }

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

    @property
    def rewards(self):
        return {
            "reward": round(self.reward, DECIMALS),
            "dev": round(self.dev, DECIMALS),
            "mn": round(self.mn, DECIMALS)
        }
