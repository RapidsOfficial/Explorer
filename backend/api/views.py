from webargs.flaskparser import use_args
from ..services import IntervalService
from ..services import TransactionService
from ..services import AddressService
from ..services import BlockService
from ..models import Transaction
from ..constants import CURRENCY
from flask import Blueprint
from .args import page_args
from .. import utils
from pony import orm

blueprint = Blueprint("api", __name__, url_prefix="/v2/")

def round_amount(amount):
    return round(amount, 8)

@blueprint.route("/latest", methods=["GET"])
@orm.db_session
def latest():
    block = BlockService.latest_block()

    return utils.response({
        "time": block.created.timestamp(),
        "blockhash": block.blockhash,
        "height": block.height,
        "reward": round_amount(block.reward)
    })

@blueprint.route("/transactions", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def transactions(args):
    transactions = TransactionService.transactions(args["page"])
    result = []

    for transaction in transactions:
        result.append({
            "height": transaction.block.height,
            "blockhash": transaction.block.blockhash,
            "timestamp": transaction.block.created.timestamp(),
            "txhash": transaction.txid,
            "fee": round_amount(transaction.fee),
            "coinstake": transaction.coinstake,
            "coinbase": transaction.coinbase,
            "amount": round_amount(transaction.amount)
        })

    return utils.response(result)

@blueprint.route("/blocks", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def blocks(args):
    blocks = BlockService.blocks(args["page"])
    result = []

    for block in blocks:
        result.append({
            "height": block.height,
            "blockhash": block.blockhash,
            "timestamp": block.created.timestamp(),
            "tx": len(block.transactions)
        })

    return utils.response(result)

@blueprint.route("/block/<string:bhash>", methods=["GET"])
@orm.db_session
def block_data(bhash):
    block = BlockService.get_by_hash(bhash)

    if block:
        return utils.response({
            "reward": round_amount(block.reward),
            "blockhash": block.blockhash,
            "height": block.height,
            "tx": len(block.transactions),
            "timestamp": block.created.timestamp(),
            "merkleroot": block.merkleroot,
            "version": block.version,
            "stake": block.stake,
            "nonce": block.nonce,
            "size": block.size,
            "bits": block.bits
        })

    return utils.dead_response("Block not found"), 404

@blueprint.route("/block/<string:bhash>/transactions", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def block_transactions_list(args, bhash):
    block = BlockService.get_by_hash(bhash)

    if block:
        transactions = block.transactions.page(args["page"])
        result = []

        for transaction in transactions:
            transaction_result = transaction.display()
            transfer = utils.make_request("gettokentransaction", [transaction.txid])

            if not transfer["error"]:
                if transfer["result"]["valid"]:
                    transfer["result"].pop("ismine")

                    transaction_result["transfer"] = transfer["result"]

            result.append(transaction_result)

        return utils.response(result)

    return utils.dead_response("Block not found"), 404

@blueprint.route("/transaction/<string:txid>", methods=["GET"])
@orm.db_session
def transaction(txid):
    transaction = TransactionService.get_by_txid(txid)

    if transaction:
        transaction_result = transaction.display()
        transfer = utils.make_request("gettokentransaction", [transaction.txid])

        if not transfer["error"]:
            if transfer["result"]["valid"]:
                transfer["result"].pop("ismine")

                transaction_result["transfer"] = transfer["result"]

        return utils.response(transaction_result)

    return utils.dead_response("Transaction not found"), 404

@blueprint.route("/history/<string:address>", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def history(args, address):
    address = AddressService.get_by_address(address)
    result = []

    if address:
        transactions = address.transactions.order_by(
            orm.desc(Transaction.id)
        ).page(args["page"], pagesize=100)

        for transaction in transactions:
            transaction_result = transaction.display()
            transfer = utils.make_request("gettokentransaction", [transaction.txid])

            if not transfer["error"]:
                if transfer["result"]["valid"]:
                    transfer["result"].pop("ismine")

                    transaction_result["transfer"] = transfer["result"]

            result.append(transaction_result)

    return utils.response(result)

@blueprint.route("/chart/<string:key>", methods=["GET"])
@orm.db_session
def chart(key):
    chart = []

    if key in ["transactions", "masternodes"]:
        intervals = IntervalService.list(key)

        for interval in intervals:
            chart.append({
                "time": str(interval.time),
                "value": interval.value,
            })

    return utils.response(chart)

@blueprint.route("/balance/<string:address>", methods=["GET"])
@orm.db_session
def balances(address):
    address = AddressService.get_by_address(address)
    result = {
        "balance": 0,
        "tokens": []
    }

    if address:
        for balance in address.balances:
            if balance.currency == CURRENCY:
                result["balance"] = round_amount(balance.balance)

        tokens = utils.make_request("getalltokenbalancesforaddress", [address.address])

        if not tokens["error"]:
            result["tokens"] = tokens["result"]

    return utils.response(result)

@blueprint.route("/token/<string:name>", methods=["GET"])
@orm.db_session
def token_info(name):
    result = utils.make_request("gettoken", [name])
    return result

# @blueprint.route("/token/<string:name>/transactions", methods=["GET"])
# @orm.db_session
# def token_transactions(name):
#     result = utils.make_request("gettoken", [name])
#     return result

@blueprint.route("/tokens", methods=["GET"])
@orm.db_session
def token_list():
    result = utils.make_request("listtokens")
    return result

@blueprint.route("/block/<string:bhash>", methods=["GET"])
@orm.db_session
def block(bhash):
    block = BlockService.get_by_hash(bhash)

    if block:
        return utils.response({
            "blockhash": block.blockhash,
            "height": block.height,
            "tx": len(block.transactions),
            "timestamp": block.created.timestamp(),
            "merkleroot": block.merkleroot,
            "version": block.version,
            "stake": block.stake,
            "nonce": block.nonce,
            "size": block.size,
            "bits": block.bits,
            "rewards": block.rewards
        })

    return utils.dead_response("Block not found"), 404
