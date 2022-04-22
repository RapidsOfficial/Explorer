from ..constants import REDUCTION_HEIGHT, BURN_ADDRESS, TOKEN_GENESIS
from ..constants import CURRENCY, DECIMALS
from ..services import TransactionService
from .utils import log_block, log_message
from ..methods.general import General
from ..services import BalanceService
from ..services import AddressService
from ..models import Token, Transfer, Trade
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
                balance.sent += prev_out.amount

                if prev_out.vin:
                    prev_out.vin.delete()

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
                    amount = round(amount / 1000, DECIMALS)

                # ToDo: Add token support here
                currency = CURRENCY

                script = vout["address"]
                if not script:
                    continue

                address = AddressService.get_by_address(script, True, created)
                address.transactions.add(transaction)
                address.lastactive = created

                output = OutputService.create(
                    transaction, amount, vout["type"],
                    address, vout["script"],
                    vout["n"], currency
                )

                if currency == CURRENCY:
                    output_amount += output.amount

                balance = BalanceService.get_by_currency(address, currency)
                balance.balance += output.amount
                balance.received += output.amount

                if currency == CURRENCY:
                    if address.address == BURN_ADDRESS:
                        burn_amount += output.amount

                    if coinstake:
                        if block.height > REDUCTION_HEIGHT and index == 1:
                            dev += output.amount

                        else:
                            if reward_address is None or reward_address == address:
                                reward_address = address
                                reward += output.amount

                        if block.height > REDUCTION_HEIGHT:
                            if index == output_count - 1:
                                mn += output.amount

                            if index == output_count:
                                dev += output.amount

                        else:
                            if index == output_count:
                                mn += output.amount

                    elif coinbase:
                        reward += output.amount

            if coinbase or coinstake or burn_amount > 0:
                supply = StatsService.get_by_key("supply")
                supply.value -= burn_amount

            if coinbase or coinstake:
                supply.value += float(reward + dev + mn)

            else:
                transaction.fee = input_amout - output_amount
                non_reward_transactions += 1

            total_transactions += 1

        # Parse tokens
        transfer_data = utils.make_request("gettokentransaction", [transaction.txid])

        # Create token
        if not transfer_data["error"] and block.height >= TOKEN_GENESIS:
            result = transfer_data["result"]

            # ToDo: add dex handling logic
            if result["type"] == "DEx Purchase":
                continue

            elif not result["valid"]:
                continue

            # Create token
            if result["type_int"] in [50, 54, 51]:
                if result["ecosystem"] != "main":
                    continue

                issuer = AddressService.get_by_address(
                    result["sendingaddress"], True, created
                )

                amount = float(result["amount"])
                managed = False if result["type_int"] == 50 else True
                crowdsale = result["type_int"] == 51

                token = Token(**{
                    "supply": amount,
                    "divisible": result["divisible"],
                    "subcategory": result["subcategory"],
                    "category": result["category"],
                    "ticker": result["propertyticker"],
                    "name": result["propertyname"],
                    "data": result["data"],
                    "url": result["url"],
                    "transaction": transaction,
                    "crowdsale": crowdsale,
                    "managed": managed,
                    "issuer": issuer
                })

                if amount > 0:
                    Transfer(**{
                        "amount": amount,
                        "transaction": transaction,
                        "receiver": issuer,
                        "token": token,
                        "create": True
                    })

                    balance_issuer = BalanceService.get_by_currency(issuer, token.ticker)
                    balance_issuer.balance += amount
                    balance_issuer.received += amount

            # Grant tokens
            elif result["type_int"] == 55:
                if not (token := Token.get(ticker=result["propertyticker"])):
                    continue

                sender = AddressService.get_by_address(
                    result["sendingaddress"], True, created
                )

                receiver = AddressService.get_by_address(
                    result["referenceaddress"], True, created
                )

                amount = float(result["amount"])

                Transfer(**{
                    "amount": amount,
                    "transaction": transaction,
                    "receiver": receiver,
                    "sender": sender,
                    "token": token,
                    "create": True
                })

                balance_receiver = BalanceService.get_by_currency(receiver, token.ticker)
                balance_receiver.balance += amount
                balance_receiver.received += amount

                token.supply += amount

            # Revoke tokens
            elif result["type_int"] == 56:
                if not (token := Token.get(ticker=result["propertyticker"])):
                    continue

                sender = AddressService.get_by_address(
                    result["sendingaddress"], True, created
                )

                amount = float(result["amount"])

                Transfer(**{
                    "amount": amount,
                    "transaction": transaction,
                    "sender": sender,
                    "token": token,
                    "burn": True
                })

                balance_sender = BalanceService.get_by_currency(sender, token.ticker)
                balance_sender.balance -= amount
                balance_sender.sent += amount

                token.supply -= amount

            # Change issuer
            elif result["type_int"] == 70:
                if not (token := Token.get(ticker=result["propertyticker"])):
                    continue

                receiver = AddressService.get_by_address(
                    result["referenceaddress"], True, created
                )

                token.issuer = receiver

            # Simple send
            elif result["type_int"] == 0:
                if not (token := Token.get(ticker=result["propertyticker"])):
                    continue

                sender = AddressService.get_by_address(
                    result["sendingaddress"], True, created
                )

                receiver = AddressService.get_by_address(
                    result["referenceaddress"], True, created
                )

                amount = float(result["amount"])
                crowdsale = result["type"] == "Crowdsale Purchase"

                Transfer(**{
                    "amount": amount,
                    "transaction": transaction,
                    "receiver": receiver,
                    "sender": sender,
                    "token": token
                })

                balance_receiver = BalanceService.get_by_currency(receiver, token.ticker)
                balance_receiver.balance += amount
                balance_receiver.received += amount

                balance_sender = BalanceService.get_by_currency(sender, token.ticker)
                balance_sender.balance -= amount
                balance_sender.sent += amount

                if crowdsale:
                    if not (crowdsale := Token.get(ticker=result["purchasedpropertyticker"])):
                        continue

                    amount = float(result["purchasedtokens"])

                    Transfer(**{
                        "amount": amount,
                        "transaction": transaction,
                        "receiver": sender,
                        "sender": receiver,
                        "token": crowdsale,
                        "crowdsale": True
                    })

                    balance_sender_crowdsale = BalanceService.get_by_currency(sender, crowdsale.ticker)
                    balance_sender_crowdsale.balance += amount
                    balance_sender_crowdsale.received += amount

            # Trade
            elif result["type_int"] == 25:
                token_trade = utils.make_request("gettokentrade", [transaction.txid])

                if not token_trade["error"] and token_trade["result"]["valid"]:
                    trade_result = token_trade["result"]

                    if len(trade_result["matches"]) == 0:
                        continue

                    if not (token_desired := Token.get(ticker=trade_result["propertytickerdesired"])):
                        continue

                    if not (token_sale := Token.get(ticker=trade_result["propertytickerforsale"])):
                        continue

                    sender = AddressService.get_by_address(
                        result["sendingaddress"], True, created
                    )

                    balance_sender_desired = BalanceService.get_by_currency(sender, token_desired.ticker)
                    balance_sender_sale = BalanceService.get_by_currency(sender, token_sale.ticker)

                    for match in trade_result["matches"]:
                        if match["block"] <= trade_result["block"]:
                            receiver = AddressService.get_by_address(
                                match["address"], True, created
                            )

                            balance_receiver_desired = BalanceService.get_by_currency(receiver, token_desired.ticker)
                            balance_receiver_sale = BalanceService.get_by_currency(receiver, token_sale.ticker)

                            amount_received = float(match["amountreceived"])
                            amount_sold = float(match["amountsold"])

                            Trade(**{
                                "receiver": receiver,
                                "sender": sender,
                                "transaction": transaction,
                                "token_desired": token_desired,
                                "token_sale": token_sale,
                                "amount_received": amount_received,
                                "amount_sold": amount_sold
                            })

                            Transfer(**{
                                "amount": amount_sold,
                                "transaction": transaction,
                                "receiver": receiver,
                                "sender": sender,
                                "token": token_sale,
                                "trade": True
                            })

                            balance_receiver_sale.balance += amount_sold
                            balance_receiver_sale.received += amount_sold

                            balance_sender_sale.balance -= amount_sold
                            balance_sender_sale.sent += amount_sold

                            Transfer(**{
                                "amount": amount_received,
                                "transaction": transaction,
                                "receiver": sender,
                                "sender": receiver,
                                "token": token_desired,
                                "trade": True
                            })

                            balance_sender_desired.balance += amount_received
                            balance_sender_desired.received += amount_received

                            balance_receiver_desired.balance -= amount_received
                            balance_receiver_desired.sent += amount_received

            # Unsupported token transaction type
            else:
                continue

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
