from ..constants import DECIMALS, CURRENCY
from .block import Block
from .base import db
from pony import orm

class Transaction(db.Entity):
    _table_ = "chain_transactions"

    coinstake = orm.Required(bool, default=False)
    coinbase = orm.Required(bool, default=False)
    fee = orm.Required(float, default=0)
    txid = orm.Required(str, index=True)
    locktime = orm.Required(int)
    size = orm.Required(int)

    block = orm.Required("Block")
    outputs = orm.Set("Output")
    inputs = orm.Set("Input")
    issued = orm.Set("Token")

    transfers = orm.Set("Transfer")
    addresses = orm.Set("Address")
    orders = orm.Set("TradeOrder")
    # trades = orm.Set("Trade")

    purchases = orm.Set("DexPurchase")
    offers = orm.Set("DexOffer")

    @property
    def vin(self):
        inputs = self.inputs.order_by(-1)
        return inputs

    @property
    def simple_vin(self):
        result = []
        tmp = {}

        for vin in self.vin:
            if vin.vout.address not in tmp:
                tmp[vin.vout.address] = 0

            tmp[vin.vout.address] += vin.vout.amount

        for address in tmp:
            result.append({
                "address": address,
                "amount": tmp[address]
            })

        return result

    @property
    def vout(self):
        outputs = self.outputs.order_by(-1)
        return outputs

    @property
    def simple_vout(self):
        result = []
        tmp = {}

        for vout in self.vout:
            if vout.address not in tmp:
                tmp[vout.address] = 0

            tmp[vout.address] += vout.amount

        for address in tmp:
            result.append({
                "address": address,
                "amount": tmp[address]
            })

        return result

    @property
    def is_reward(self):
        return self.coinstake or self.coinbase

    @property
    def amount(self):
        output_amount = 0

        if self.is_reward:
            output_amount += (
                self.block.reward + self.block.dev + self.block.mn
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

    @property
    def input_amount(self):
        total = 0

        for vin in self.inputs:
            total += vin.vout.amount

        return total

    @property
    def output_amount(self):
        total = 0

        for vout in self.outputs:
            total += vout.amount

        return total

    @property
    def display(self):
        latest_blocks = Block.select().order_by(
            orm.desc(Block.height)
        ).first()

        output_amount = 0
        input_amount = 0
        transfers = []
        issued = []
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

        for token in self.issued:
            issued.append(token.display)

        for transfer in self.transfers:
            transfers.append(transfer.display)

        if not self.coinbase and not self.coinstake:
            fee = input_amount - output_amount

        return {
            "amount": round(output_amount, DECIMALS),
            "confirmations": latest_blocks.height - self.block.height + 1,
            "fee": round(fee, DECIMALS),
            "coinstake": self.coinstake,
            "blockhash": self.block.blockhash,
            "timestamp": int(self.block.created.timestamp()),
            "height": self.block.height,
            "coinbase": self.coinbase,
            "txid": self.txid,
            "size": self.size,
            "outputs": outputs,
            "mempool": False,
            "inputs": inputs,
            "issued": issued,
            "transfers": transfers
        }

    @property
    def simple_display(self):
        latest_blocks = Block.select().order_by(
            orm.desc(Block.height)
        ).first()

        currency = CURRENCY
        amount = 0

        for vout in self.outputs:
            if vout.currency == CURRENCY:
                amount += vout.amount

        for transfer in self.transfers:
            amount = transfer.amount
            currency = transfer.token.name

        return {
            "amount": round(amount, DECIMALS),
            "confirmations": latest_blocks.height - self.block.height + 1,
            "timestamp": int(self.block.created.timestamp()),
            "txid": self.txid,
            "token": currency
        }
