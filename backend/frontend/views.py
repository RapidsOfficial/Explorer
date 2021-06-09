from ..services import TransactionService
from ..services import AddressService
from ..services import BlockService
from flask import redirect, url_for
from flask import render_template
from flask import Blueprint
from pony import orm

from webargs.flaskparser import use_args
from webargs import fields

blueprint = Blueprint("frontend", __name__)

@blueprint.route("/")
@orm.db_session
def home():
    blocks = BlockService.blocks(size=100)
    return render_template("pages/overview.html", blocks=blocks)

@blueprint.route("/block/<string:blockhash>")
@orm.db_session
def block(blockhash):
    block = BlockService.get_by_hash(blockhash)
    return render_template("pages/block.html", block=block)

@blueprint.route("/height/<int:height>")
@orm.db_session
def height(height):
    if (block := BlockService.get_by_height(height)):
        return redirect(url_for("frontend.block", blockhash=block.blockhash))

    return redirect(url_for("frontend.home"))

# ToDo: Height endpoint

@blueprint.route("/transactions")
@orm.db_session
def transactions():
    transactions = TransactionService.transactions(size=100)
    return render_template("pages/transactions.html", transactions=transactions)

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
@use_args({"query": fields.Str(required=True)}, location="query")
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
