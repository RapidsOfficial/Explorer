from .constants import REDUCTION_HEIGHT, DECIMALS, CURRENCY
from datetime import datetime
from pony import orm

db = orm.Database("sqlite", "../rapids.db", create_db=True)

class Stats(db.Entity):
    _table_ = "chain_stats"

    value = orm.Required(float, default=0)
    key = orm.Required(str, index=True)

class Peer(db.Entity):
    _table_ = "chain_peers"

    created = orm.Required(datetime, default=datetime.utcnow)
    protocol = orm.Required(str)
    version = orm.Required(str)
    address = orm.Required(str)

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

    # ToDo: Remove this
    reward = orm.Required(float, default=0)
    dev = orm.Required(float, default=0)
    mn = orm.Required(float, default=0)

    previous_block = orm.Optional("Block")
    transactions = orm.Set("Transaction")
    next_block = orm.Optional("Block")

    @property
    def txs(self):
        transactions = self.transactions.order_by(1)
        return transactions

    @property
    def timestamp(self):
        return int(self.created.timestamp())

    @property
    def txcount(self):
        return len(self.transactions)

    @property
    def confirmations(self):
        latest_blocks = Block.select().order_by(
            orm.desc(Block.height)
        ).first()

        return latest_blocks.height - self.height + 1

    @property
    def rewards(self):
        reward = 0
        dev = 0
        mn = 0

        transaction = self.transactions.select().first()

        if transaction.coinstake:
            reward_address = None

            for index, vout in enumerate(transaction.outputs.order_by(Output.n)):
                if self.height > REDUCTION_HEIGHT and index == 0:
                    dev += vout.amount

                else:
                    if reward_address is None or reward_address == vout.address:
                        reward_address = vout.address
                        reward += vout.amount

                if self.height > REDUCTION_HEIGHT:
                    if index == len(transaction.outputs) - 1:
                        mn += vout.amount

                    if index == len(transaction.outputs):
                        dev += vout.amount

                else:
                    if index == len(transaction.outputs):
                        mn += vout.amount

            for vin in transaction.inputs:
                reward -= vin.vout.amount

        else:
            for vout in transaction.outputs:
                reward += vout.amount

        return {
            "reward": round(reward, DECIMALS),
            "dev": round(dev, DECIMALS),
            "mn": round(mn, DECIMALS)
        }

class Transaction(db.Entity):
    _table_ = "chain_transactions"

    coinstake = orm.Required(bool, default=False)
    coinbase = orm.Required(bool, default=False)
    txid = orm.Required(str, index=True)
    locktime = orm.Required(int)
    size = orm.Required(int)

    block = orm.Required("Block")
    outputs = orm.Set("Output")
    inputs = orm.Set("Input")

    addresses = orm.Set("Address")

    @property
    def vin(self):
        inputs = self.inputs.order_by(-1)
        return inputs

    @property
    def vout(self):
        outputs = self.outputs.order_by(-1)
        return outputs

    @property
    def is_reward(self):
        return self.coinstake or self.coinbase

    @property
    def amount(self):
        output_amount = 0

        if self.is_reward:
            rewards = self.block.rewards
            output_amount += (
                rewards["reward"] + rewards["dev"] + rewards["mn"]
            )

        else:
            for vout in self.outputs:
                if vout.currency == CURRENCY:
                    output_amount += vout.amount

        return round(output_amount, DECIMALS)

    @property
    def currencies(self):
        result = []

        for output in self.outputs:
            if output.currency not in result:
                result.append(output.currency)

        return result

    def display(self):
        latest_blocks = Block.select().order_by(
            orm.desc(Block.height)
        ).first()

        output_amount = 0
        input_amount = 0
        outputs = []
        inputs = []
        fee = 0

        for vin in self.inputs:
            inputs.append({
                "address": vin.vout.address.address,
                "currency": vin.vout.currency,
                "amount": round(vin.vout.amount, DECIMALS)
            })

            if vin.vout.currency == CURRENCY:
                input_amount += vin.vout.amount

        for vout in self.outputs:
            outputs.append({
                "address": vout.address.address,
                "currency": vout.currency,
                "amount": round(vout.amount, DECIMALS),
                "category": vout.category
            })

            if vout.currency == CURRENCY:
                output_amount += vout.amount

        if not self.coinbase and not self.coinstake:
            fee = input_amount - output_amount

        return {
            "amount": round(output_amount, DECIMALS),
            "confirmations": latest_blocks.height - self.block.height + 1,
            "fee": round(fee, DECIMALS),
            "coinstake": self.coinstake,
            "height": self.block.height,
            "coinbase": self.coinbase,
            "txid": self.txid,
            "size": self.size,
            "outputs": outputs,
            "mempool": False,
            "inputs": inputs
        }

class Address(db.Entity):
    _table_ = "chain_addresses"

    # ToDo: Created/last active
    # ToDo: POS info

    address = orm.Required(str, index=True)
    outputs = orm.Set("Output")

    transactions = orm.Set(
        "Transaction", table="chain_address_transactions",
        reverse="addresses"
    )

    balances = orm.Set("Balance")

class Balance(db.Entity):
    _table_ = "chain_address_balance"

    # ToDo: Received/Sent

    balance = orm.Required(float, default=0)
    address = orm.Required("Address")
    currency = orm.Required(str)

    orm.composite_index(address, currency)

class Input(db.Entity):
    _table_ = "chain_inputs"

    sequence = orm.Required(int, size=64)
    n = orm.Required(int)

    transaction = orm.Required("Transaction")
    vout = orm.Required("Output")

    def before_delete(self):
        balance = Balance.get(
            address=self.vout.address, currency=self.vout.currency
        )

        balance.balance += self.vout.amount

class Output(db.Entity):
    _table_ = "chain_outputs"

    amount = orm.Required(float)
    currency = orm.Required(str, default=CURRENCY, index=True)
    address = orm.Required("Address")
    category = orm.Optional(str)
    raw = orm.Optional(str)
    n = orm.Required(int)

    vin = orm.Optional("Input", cascade_delete=True)
    transaction = orm.Required("Transaction")
    address = orm.Optional("Address")

    @property
    def spent(self):
        return self.vin is not None

    def before_delete(self):
        balance = Balance.get(
            address=self.address, currency=self.currency
        )

        balance.balance -= self.amount

        if self.vin:
            self.vin.delete()

    orm.composite_index(transaction, n)


db.generate_mapping(create_tables=True)
