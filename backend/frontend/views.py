from ..services import TransactionService
from webargs.flaskparser import use_args
from ..services import AddressService
from ..services import BlockService
from flask import redirect, url_for
from flask import render_template
from flask import Blueprint
from pony import orm

from .args import search_args, page_args
from .. import utils
import math

blueprint = Blueprint("frontend", __name__)

@blueprint.route("/")
@use_args(page_args, location="query")
@orm.db_session
def home(args):
    page, size = args["page"], 100
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

@blueprint.route("/transactions")
@use_args(page_args, location="query")
@orm.db_session
def transactions(args):
    page, size = args["page"], 100

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

@blueprint.route("/block/<string:blockhash>")
@orm.db_session
def block(blockhash):
    page, size = 1, 10

    block = BlockService.get_by_hash(blockhash)
    transactions = block.txs.page(page, pagesize=size)

    # total = math.ceil(block.txcount / size)
    # pagination = utils.pagination(
    #     "frontend.home", page,
    #     size, total
    # )

    return render_template(
        "pages/block.html", block=block,
        transactions=transactions
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

@blueprint.route("/address/<string:address>")
@orm.db_session
def address(address):
    address = AddressService.get_by_address(address)
    return render_template("pages/address.html", address=address)

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

@blueprint.route("/masternodes")
def masternodes():
    return render_template("layout.html")

@blueprint.route("/holders")
@orm.db_session
def holders():
    richlist = AddressService.richlist()
    return render_template("pages/holders.html", richlist=richlist)

@blueprint.route("/network")
def network():
    return render_template("layout.html")

@blueprint.route("/docs")
def docs():
    return render_template("layout.html")
