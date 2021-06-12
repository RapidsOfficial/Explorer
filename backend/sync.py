from .constants import REDUCTION_HEIGHT, BURN_ADDRESS, CURRENCY
from .services import TransactionService
from .methods.general import General
from .services import BalanceService
from .services import AddressService
from .services import OutputService
from .services import InputService
from .services import BlockService
from .services import StatsService
from .services import PeerService
from .methods.block import Block
from datetime import datetime
from pony import orm
from . import parser
from . import utils

def log_block(message, block, tx=[]):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time = block.created.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} {message}: hash={block.blockhash} height={block.height} tx={len(tx)} date='{time}'")

def log_message(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} {message}")

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
def sync_peers():
    peers = General.peers()

    if peers["error"] is None:
        knows_peers = PeerService.list()
        for peer in knows_peers:
            peer.active = False

        for peer in peers["result"]:
            address, port = peer["addr"].split(":")
            version = peer["version"]
            subver = peer["subver"]

            if address[0] == "[":
                continue

            if not subver:
                continue

            if (knows_peer := PeerService.get_by_address(address)):
                knows_peer.active = True

            else:
                # ToDo: get country here
                PeerService.create(address, port, version, subver)

        # ToDo: peer historical data

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

        for tx in txs:
            if block.stake and tx["index"] == 0:
                continue

            coinbase = block.stake is False and tx["index"] == 0
            coinstake = block.stake and tx["index"] == 1

            transaction = TransactionService.create(
                tx["txid"], tx["locktime"], tx["size"],
                block, coinbase, coinstake
            )

            input_amout = 0

            for vin in tx["inputs"]:
                if vin["coinbase"]:
                    continue

                prev_tx = TransactionService.get_by_txid(vin["txid"])
                prev_out = OutputService.get_by_prev(prev_tx, vin["vout"])

                prev_out.address.transactions.add(transaction)
                balance = BalanceService.get_by_currency(prev_out.address, prev_out.currency)
                balance.balance -= prev_out.amount

                if coinbase or coinstake:
                    input_amout += prev_out.amount

                if not prev_out:
                    print(vin["txid"])

                InputService.create(
                    vin["sequence"], vin["vout"], transaction, prev_out
                )

            burn_amount = 0

            for vout in tx["outputs"]:
                if not vout["type"]:
                    continue

                amount = utils.amount(vout["value"])
                if height <= REDUCTION_HEIGHT:
                    amount /= 1000

                currency = CURRENCY

                # ToDo: Add token support here

                script = vout["address"]
                address = AddressService.get_by_address(script, True)
                address.transactions.add(transaction)

                output = OutputService.create(
                    transaction, amount, vout["type"],
                    address, vout["script"],
                    vout["n"], currency
                )

                balance = BalanceService.get_by_currency(address, currency)
                balance.balance += output.amount

                if address.address == BURN_ADDRESS:
                    burn_amount += amount

            if coinbase or coinstake or burn_amount > 0:
                supply = StatsService.get_by_key("supply")
                supply.value -= burn_amount

            if coinbase or coinstake:
                supply.value += block.reward + block.dev + block.mn

            else:
                non_reward_transactions += 1

        # ToDo: Count transactions here

        # ToDo: Count addresses here?

        # ToDo: Store block tx count here

        # ToDo: Decimals

        if non_reward_transactions > 0:
            transactions = StatsService.get_by_key("transactions")
            transactions.value += non_reward_transactions

        latest_block = block
        orm.commit()
