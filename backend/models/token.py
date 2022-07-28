from .balance import Balance
from .base import db
from pony import orm

class Token(db.Entity):
    _table_ = "chain_tokens"

    subcategory = orm.Optional(str, nullable=True)
    category = orm.Optional(str, nullable=True)
    data = orm.Optional(str, nullable=True)
    url = orm.Optional(str, nullable=True)
    supply = orm.Required(float, default=0)
    ticker = orm.Required(str, index=True)
    divisible = orm.Required(bool)
    crowdsale = orm.Required(bool)
    managed = orm.Required(bool)
    name = orm.Required(str)

    transaction = orm.Required("Transaction")
    issuer = orm.Required("Address")
    transfers = orm.Set("Transfer")

    # trades_desierd = orm.Set("Trade", reverse="token_desired")
    # trades_sold = orm.Set("Trade", reverse="token_sale")

    @property
    def nft(self):
        return (not self.divisible and self.supply == 1)

    @property
    def display(self):
        holders = Balance.select(
            lambda b: b.currency == self.name
        ).count(distinct=False)

        return {
            "transaction": self.transaction.txid,
            "subcategory": self.subcategory,
            "issuer": self.issuer.address,
            "divisible": self.divisible,
            "crowdsale": self.crowdsale,
            "category": self.category,
            "managed": self.managed,
            "supply": self.supply,
            "holders": holders,
            "ticker": self.ticker,
            "name": self.name,
            "data": self.data,
            "url": self.url,
            "nft": self.nft
        }

class Transfer(db.Entity):
    _table_ = "chain_transfers"

    transaction = orm.Required("Transaction")
    crowdsale = orm.Required(bool, default=False)
    create = orm.Required(bool, default=False)
    trade = orm.Required(bool, default=False)
    burn = orm.Required(bool, default=False)
    amount = orm.Required(float, default=0)

    receiver = orm.Optional("Address", reverse="received")
    sender = orm.Optional("Address", reverse="sent")
    token = orm.Required("Token")

    def before_delete(self):
        # Grant tokens
        # if self.create:
        #     self.token.supply -= self.amount

        # Revoke tokens
        if self.burn:
            self.token.supply += self.amount

        if self.receiver:
            balance_receiver = Balance.get(
                address=self.receiver, currency=self.token.name
            )

            if balance_receiver:
                balance_receiver.balance -= self.amount
                balance_receiver.received -= self.amount

        if self.sender and not self.crowdsale:
            balance_sender = Balance.get(
                address=self.sender, currency=self.token.name
            )

            if balance_sender:
                balance_sender.balance += self.amount
                balance_sender.sent -= self.amount

    @property
    def display(self):
        receiver = self.receiver.address if self.receiver else None
        sender = self.sender.address if self.sender else None

        return {
            "timestamp": int(self.transaction.block.created.timestamp()),
            "transaction": self.transaction.txid,
            "crowdsale": self.crowdsale,
            "token": self.token.name,
            "create": self.create,
            "amount": self.amount,
            "burn": self.burn,
            "receiver": receiver,
            "sender": sender
        }

# class Trade(db.Entity):
#     _table_ = "chain_trades"

#     receiver = orm.Optional("Address", reverse="trades_received")
#     sender = orm.Optional("Address", reverse="trades_sent")
#     transaction = orm.Required("Transaction")

#     token_desired = orm.Required("Token", reverse="trades_desierd")
#     token_sale = orm.Required("Token", reverse="trades_sold")

#     amount_received = orm.Required(float, default=0)
#     amount_sold = orm.Required(float, default=0)
