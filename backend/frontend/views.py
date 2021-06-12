from ..services import TransactionService
from webargs.flaskparser import use_args
from ..services import AddressService
from ..services import BlockService
from flask import redirect, url_for
from ..services import PeerService
from flask import render_template
from flask import Blueprint
from pony import orm

from .args import search_args
from .. import utils
import math

blueprint = Blueprint("frontend", __name__)

@blueprint.route("/", defaults={"page": 1})
@blueprint.route("/<int:page>")
@orm.db_session
def home(page):
    size = 30
    latest = BlockService.latest_block()
    total = math.ceil(latest.height / size)

    blocks = BlockService.blocks(page=page, size=size)
    pagination = utils.pagination(
        "frontend.home", page,
        size, total
    )

    return render_template(
        "pages/overview.html", pagination=pagination,
        blocks=blocks
    )

@blueprint.route("/transactions", defaults={"page": 1})
@blueprint.route("/transactions/<int:page>")
@orm.db_session
def transactions(page):
    size = 100

    transactions = TransactionService.transactions(page=page, size=size)
    count = TransactionService.count()
    total = math.ceil(count / size)

    pagination = utils.pagination(
        "frontend.transactions", page,
        size, total
    )

    return render_template(
        "pages/transactions.html", pagination=pagination,
        transactions=transactions
    )

@blueprint.route("/block/<string:blockhash>", defaults={"page": 1})
@blueprint.route("/block/<string:blockhash>/<int:page>")
@orm.db_session
def block(blockhash, page):
    size = 10
    block = BlockService.get_by_hash(blockhash)
    transactions = block.txs.page(page, pagesize=size)

    total = math.ceil(block.txcount / size)
    pagination = utils.pagination(
        "frontend.block", page,
        size, total
    )

    return render_template(
        "pages/block.html", block=block,
        transactions=transactions,
        pagination=pagination
    )

@blueprint.route("/height/<int:height>")
@orm.db_session
def height(height):
    if (block := BlockService.get_by_height(height)):
        return redirect(url_for("frontend.block", blockhash=block.blockhash))

    return redirect(url_for("frontend.home"))

@blueprint.route("/transaction/<string:txid>")
@orm.db_session
def transaction(txid):
    transaction = TransactionService.get_by_txid(txid)
    return render_template("pages/transaction.html", transaction=transaction)

@blueprint.route("/address/<string:address>", defaults={"page": 1})
@blueprint.route("/address/<string:address>/<int:page>")
@orm.db_session
def address(address, page):
    address = AddressService.get_by_address(address)

    # ToDo: transactions pagination

    size = 10
    transactions = address.txs.page(page, pagesize=size)

    total = math.ceil(address.txcount / size)
    pagination = utils.pagination(
        "frontend.address", page,
        size, total
    )

    return render_template(
        "pages/address.html", address=address,
        transactions=transactions,
        pagination=pagination
    )

@blueprint.route("/search")
@use_args(search_args, location="query")
@orm.db_session
def search(args):
    if args["query"].isdigit():
        if (block := BlockService.get_by_height(args["query"])):
            return redirect(url_for("frontend.block", blockhash=block.blockhash))

    else:
        if len(args["query"]) == 64:
            if (block := BlockService.get_by_hash(args["query"])):
                return redirect(url_for("frontend.block", blockhash=block.blockhash))

            return redirect(url_for("frontend.transaction", txid=args["query"]))

        else:
            return redirect(url_for("frontend.address", address=args["query"]))

    return redirect(url_for("frontend.home"))

@blueprint.route("/holders", defaults={"page": 1})
@blueprint.route("/holders/<int:page>")
@orm.db_session
def holders(page):
    total = 10
    size = 100

    addresses = AddressService.richlist(page, size)
    richlist = []

    pagination = utils.pagination(
        "frontend.holders", page,
        size, total
    )

    for index, entry in enumerate(addresses):
        richlist.append({
            "index": (index + 1) + ((page - 1) * size),
            "address": entry[0].address,
            "balance": float(entry[1])
        })

    return render_template(
        "pages/holders.html", richlist=richlist,
        pagination=pagination
    )

@blueprint.route("/masternodes")
def masternodes():
    return render_template("layout.html")

@blueprint.route("/network")
@orm.db_session
def network():
    peers = PeerService.list(True)
    return render_template(
        "pages/peers.html", peers=peers
    )

@blueprint.route("/docs")
def docs():
    return render_template("layout.html")
