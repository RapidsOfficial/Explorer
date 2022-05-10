from .args import masternodes_args, filter_args
from .args import page_args, search_args
from ..models import Token, Address, Block
from ..models import Transaction, Balance
from ..services import TransactionService
from webargs.flaskparser import use_args
from ..services import MasternodeService
from ..services import IntervalService
from ..services import AddressService
from ..services import StatsService
from ..services import BlockService
from ..constants import CURRENCY
from flask import Blueprint
from .. import utils
from pony import orm

blueprint = Blueprint("api", __name__, url_prefix="/v2/")

@blueprint.route("/latest", methods=["GET"])
@orm.db_session
def latest():
    block = BlockService.latest_block()

    return utils.response(block.display)

@blueprint.route("/masternodes/stats", methods=["GET"])
@orm.db_session
def masternodes_stats():
    masternodes = MasternodeService.total()
    collateral = 10000

    return utils.response({
        "locked": collateral * masternodes,
        "collateral": collateral,
        "count": masternodes
    })

@blueprint.route("/masternodes", methods=["GET"])
@use_args(masternodes_args, location="query")
@orm.db_session
def masternodes(args):
    masternodes = MasternodeService.list()
    masternodes = masternodes.order_by(lambda m: m.rank)

    if args["filter"]:
        masternodes = masternodes.filter(lambda m: m.status == args["filter"])

    masternodes = masternodes.page(args["page"], pagesize=100)
    result = []

    for masternode in masternodes:
        result.append(masternode.display)

    return utils.response(result)

@blueprint.route("/search", methods=["GET"])
@use_args(search_args, location="query")
@orm.db_session
def search(args):
    result = []

    if args["query"] and len(args["query"]) >= 3:
        transactions = Transaction.select(
            lambda t: t.txid.startswith(args["query"])
        ).limit(3)

        for transaction in transactions:
            result.append({
                "result": transaction.txid,
                "type": "transaction"
            })

        blocks = Block.select(
            lambda b: b.blockhash.startswith(args["query"])
        ).limit(3)

        for block in blocks:
            result.append({
                "result": block.blockhash,
                "type": "block"
            })

        addresses = Address.select(
            lambda a: a.address.startswith(args["query"])
        ).limit(3)

        for address in addresses:
            result.append({
                "result": address.address,
                "type": "address"
            })

        tokens = Token.select(
            lambda t: t.ticker.startswith(args["query"])
        ).limit(3)

        for token in tokens:
            result.append({
                "result": token.ticker,
                "type": "token"
            })

    return utils.response(result)

@blueprint.route("/transactions", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def transactions(args):
    transactions = TransactionService.transactions(args["page"])
    result = []

    for transaction in transactions:
        result.append(transaction.simple_display)

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
        "lastactive": 0,
        "created": 0,
        "tokens": []
    }

    if address:
        result["lastactive"] = int(address.lastactive.timestamp())
        result["created"] = int(address.created.timestamp())

        for balance in address.balances:
            if balance.currency == CURRENCY:
                result["balance"] = utils.round_amount(balance.balance)
                result["received"] = utils.round_amount(balance.received)
                result["sent"] = utils.round_amount(balance.sent)

            else:
                result["tokens"].append({
                    "token": balance.currency,
                    "balance": utils.round_amount(balance.balance),
                    "received": utils.round_amount(balance.received),
                    "sent": utils.round_amount(balance.sent)
                })

    return utils.response(result)

@blueprint.route("/token/<string:ticker>", methods=["GET"])
@orm.db_session
def token_info(ticker):
    if ticker == "RPD":
        supply = StatsService.get_by_key("supply").value

        holders = Balance.select(
            lambda b: b.currency == ticker
        ).count(distinct=False)

        return {
            "category": "",
            "crowdsale": False,
            "data": "",
            "divisible": True,
            "holders": holders,
            "issuer": "Rv3LUP88ndMLMdVkhTZiJPjosm4RhdVMMP",
            "managed": False,
            "name": "Rapids",
            "ticker": "RPD",
            "nft": False,
            "subcategory": "",
            "supply": utils.round_amount(supply),
            "transaction": "094e1a19549054812eead969c70ab1bbf565bc2bd7a475273c037039a5bf6e24",
            "url": "https://rapidsnetwork.io"
        }

    if not (token := Token.get(ticker=ticker)):
        return utils.dead_response("Token not found"), 404

    return utils.response(token.display)

@blueprint.route("/token/<string:ticker>/transfers", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def token_transactions(args, ticker):
    if not (token := Token.get(ticker=ticker)):
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
    tokens = Token.select()

    if args["nft"]:
        tokens = tokens.filter(lambda t: not t.divisible and t.supply == 1)
    else:
        tokens = tokens.filter(lambda t: t.supply > 1)

    if args["search"]:
        tokens = tokens.filter(lambda t: args["search"] in t.ticker)

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

@blueprint.route("/holders", defaults={"ticker": CURRENCY}, methods=["GET"])
@blueprint.route("/holders/<string:ticker>", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def holders(args, ticker):
    holders = Balance.select(
        lambda b: b.currency == ticker
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
