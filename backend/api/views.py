from webargs.flaskparser import use_args
from ..services import IntervalService
from ..services import TransactionService
from ..services import AddressService
from ..services import BlockService
from ..models import Transaction, Token
from ..constants import CURRENCY
from flask import Blueprint
from .args import page_args
from .. import utils
from pony import orm

blueprint = Blueprint("api", __name__, url_prefix="/v2/")

@blueprint.route("/latest", methods=["GET"])
@orm.db_session
def latest():
    block = BlockService.latest_block()

    return utils.response(block.display)

@blueprint.route("/transactions", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def transactions(args):
    transactions = TransactionService.transactions(args["page"])
    result = []

    for transaction in transactions:
        result.append(transaction.display)

    return utils.response(result)

@blueprint.route("/blocks", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def blocks(args):
    blocks = BlockService.blocks(args["page"])
    result = []

    for block in blocks:
        result.append(block.display)

    return utils.response(result)

@blueprint.route("/block/<string:bhash>", methods=["GET"])
@orm.db_session
def block_data(bhash):
    block = BlockService.get_by_hash(bhash)

    if block:
        return utils.response(block.display)

    return utils.dead_response("Block not found"), 404

@blueprint.route("/block/<string:bhash>/transactions", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def block_transactions_list(args, bhash):
    block = BlockService.get_by_hash(bhash)

    if block:
        transactions = block.transactions.page(args["page"], pagesize=100)
        result = []

        for transaction in transactions:
            result.append(transaction.display)

        return utils.response(result)

    return utils.dead_response("Block not found"), 404

@blueprint.route("/transaction/<string:txid>", methods=["GET"])
@orm.db_session
def transaction(txid):
    transaction = TransactionService.get_by_txid(txid)

    if transaction:
        return utils.response(transaction.display)

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
            result.append(transaction.display)

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
                result["balance"] = utils.round_amount(balance.balance)

        tokens = utils.make_request("getalltokenbalancesforaddress", [address.address])

        if not tokens["error"]:
            tokens_list = []

            for token in tokens["result"]:
                tokens_list.append({
                    "balance": float(token["balance"]),
                    "frozen": float(token["frozen"]),
                    "reserved": float(token["reserved"]),
                    "name": token["name"]
                })

            result["tokens"] = tokens_list

    return utils.response(result)

@blueprint.route("/token/<string:name>", methods=["GET"])
@orm.db_session
def token_info(name):
    if not (token := Token.get(name=name)):
        return utils.dead_response("Token not found"), 404

    return utils.response(token.display)

@blueprint.route("/token/<string:name>/transfers", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def token_transactions(args, name):
    if not (token := Token.get(name=name)):
        return utils.dead_response("Token not found"), 404

    transfers = token.transfers.page(args["page"], pagesize=100)
    result = []

    for transfer in transfers:
        result.append(transfer.display)

    return utils.response(result)

@blueprint.route("/tokens", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def token_list(args):
    tokens = Token.select().page(args["page"], pagesize=100)
    result = []

    for token in tokens:
        result.append(token.display)

    return utils.response(result)

@blueprint.route("/nft", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def nft_list(args):
    tokens = Token.select(
        lambda t: t.nft is True
    ).page(args["page"], pagesize=100)
    result = []

    for token in tokens:
        result.append(token.display)

    return utils.response(result)
