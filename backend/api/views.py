from ..models import Transaction, Token, Balance
from webargs.flaskparser import use_args
from ..services import IntervalService
from ..services import TransactionService
from ..services import AddressService
from ..services import BlockService
from ..constants import CURRENCY
from flask import Blueprint
from .args import page_args, filter_args
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
        "received": 0,
        "sent": 0,
        "tokens": []
    }

    if address:
        for balance in address.balances:
            if balance.currency == CURRENCY:
                result["balance"] = utils.round_amount(balance.balance)

            else:
                result["tokens"].append({
                    "token": balance.currency,
                    "balance": balance.balance,
                    "received": balance.received,
                    "sent": balance.sent
                })

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
@use_args(filter_args, location="query")
@orm.db_session
def token_list(args):
    tokens = Token.select(lambda t: t.nft == args["nft"])

    if args["search"]:
        tokens = tokens.filter(lambda t: args["search"] in t.name)

    if args["category"]:
        tokens = tokens.filter(lambda t: t.category == args["category"])

    if args["subcategory"]:
        tokens = tokens.filter(lambda t: t.subcategory == args["subcategory"])

    if args["issuer"]:
        if not (issuer := AddressService.get_by_address(args["issuer"])):
            return utils.response([])

        tokens = tokens.filter(lambda t: t.issuer == issuer)

    tokens = tokens.page(args["page"], pagesize=100)
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

@blueprint.route("/holders", defaults={"name": CURRENCY}, methods=["GET"])
@blueprint.route("/holders/<string:name>", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def holders(args, name):
    holders = Balance.select(
        lambda b: b.currency == name
    ).order_by(
        orm.desc(Balance.balance)
    ).page(args["page"], pagesize=100)
    result = []

    for holder in holders:
        result.append({
            "balance": holder.balance,
            "received": holder.received,
            "sent": holder.sent,
            "address": holder.address.address
        })

    return utils.response(result)
