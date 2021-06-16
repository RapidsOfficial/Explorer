from ..constants import REDUCTION_HEIGHT, BURN_ADDRESS, CURRENCY
from ..services import TransactionService
from .utils import log_block, log_message
from ..methods.general import General
from ..services import BalanceService
from ..services import AddressService
from ..services import OutputService
from ..services import InputService
from ..services import BlockService
from ..services import StatsService
from ..methods.block import Block
from datetime import datetime
from pony import orm
from .. import utils
from . import parser

@orm.db_session
def rollback_blocks(height):
    latest_block = BlockService.latest_block()

    while latest_block.height >= height:
        log_block("Found reorg", latest_block)

        reorg_block = latest_block
        latest_block = reorg_block.previous_block

        reorg_block.delete()
        orm.commit()

    log_message("Finised rollback")

@orm.db_session
def sync_blocks():
    if not BlockService.latest_block():
        genesis_height = 0

        block_hash = Block.blockhash(genesis_height)
        raw_block = Block.raw(block_hash)

        header, txs = parser.process(raw_block)
        created = datetime.fromtimestamp(header["timestamp"])

        block = BlockService.create(
            block_hash, genesis_height, created,
            header["merkle"], header["version"], header["stake"],
            header["nonce"], header["size"],
            header["bits"]
        )

        log_block("Genesis block", block)

        orm.commit()

    current_height = General.current_height()
    latest_block = BlockService.latest_block()

    log_message(f"Current node height: {current_height}, db height: {latest_block.height}")

    while latest_block.blockhash != Block.blockhash(latest_block.height):
        log_block("Found reorg", latest_block)

        reorg_block = latest_block
        latest_block = reorg_block.previous_block

        reorg_block.delete()
        orm.commit()

    for height in range(latest_block.height + 1, current_height + 1):
        block_hash = Block.blockhash(height)
        raw_block = Block.raw(block_hash)

        header, txs = parser.process(raw_block)
        created = datetime.fromtimestamp(header["timestamp"])

        block = BlockService.create(
            block_hash, height, created,
            header["merkle"], header["version"], header["stake"],
            header["nonce"], header["size"],
            header["bits"]
        )

        block.previous_block = latest_block

        log_block("New block", block, txs)

        non_reward_transactions = 0
        total_transactions = 0

        reward = 0
        dev = 0
        mn = 0

        for tx in txs:
            if block.stake and tx["index"] == 0:
                continue

            coinbase = block.stake is False and tx["index"] == 0
            coinstake = block.stake and tx["index"] == 1

            transaction = TransactionService.create(
                tx["txid"], tx["locktime"], tx["size"],
                block, coinbase, coinstake
            )

            output_amount = 0
            input_amout = 0
            burn_amount = 0

            reward_address = None

            for vin in tx["inputs"]:
                if vin["coinbase"]:
                    continue

                prev_tx = TransactionService.get_by_txid(vin["txid"])
                prev_out = OutputService.get_by_prev(prev_tx, vin["vout"])

                prev_out.address.transactions.add(transaction)
                balance = BalanceService.get_by_currency(prev_out.address, prev_out.currency)
                prev_out.address.lastactive = created
                balance.balance -= prev_out.amount

                InputService.create(
                    vin["sequence"], vin["vout"], transaction, prev_out
                )

                if prev_out.currency == CURRENCY:
                    input_amout += prev_out.amount

                    if coinstake:
                        reward -= prev_out.amount

            output_count = len(tx["outputs"])

            for index, vout in enumerate(tx["outputs"]):
                if not vout["type"]:
                    continue

                amount = utils.amount(vout["value"])
                if height <= REDUCTION_HEIGHT:
                    amount /= 1000

                # ToDo: Add token support here
                currency = CURRENCY

                script = vout["address"]
                address = AddressService.get_by_address(script, True, created)
                address.transactions.add(transaction)
                address.lastactive = created

                if currency == CURRENCY:
                    output_amount += amount

                output = OutputService.create(
                    transaction, amount, vout["type"],
                    address, vout["script"],
                    vout["n"], currency
                )

                balance = BalanceService.get_by_currency(address, currency)
                balance.balance += output.amount

                if currency == CURRENCY:
                    if address.address == BURN_ADDRESS:
                        burn_amount += amount

                    if coinstake:
                        if block.height > REDUCTION_HEIGHT and index == 1:
                            dev += amount

                        else:
                            if reward_address is None or reward_address == address:
                                reward_address = address
                                reward += amount

                        if block.height > REDUCTION_HEIGHT:
                            if index == output_count - 1:
                                mn += amount

                            if index == output_count:
                                dev += amount

                        else:
                            if index == output_count:
                                mn += amount

                    elif coinbase:
                        reward += amount

            if coinbase or coinstake or burn_amount > 0:
                supply = StatsService.get_by_key("supply")
                supply.value -= burn_amount

            if coinbase or coinstake:
                supply.value += reward + dev + mn

            else:
                transaction.fee = input_amout - output_amount
                non_reward_transactions += 1

            total_transactions += 1

        # ToDo: Decimals?

        if non_reward_transactions > 0:
            transactions = StatsService.get_by_key("non_reward_transactions")
            transactions.value += non_reward_transactions

        if total_transactions > 0:
            transactions = StatsService.get_by_key("total_transactions")
            transactions.value += total_transactions

        block.reward = reward
        block.dev = dev
        block.mn = mn

        latest_block = block
        orm.commit()
