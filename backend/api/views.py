from webargs.flaskparser import use_args
from ..services import IntervalService
from ..services import BlockService
from flask import Blueprint
from .args import page_args
from .. import utils
from pony import orm

blueprint = Blueprint("api", __name__, url_prefix="/v2/")

@blueprint.route("/chart/transactions", methods=["GET"])
@orm.db_session
def chart_transactions():
    intervals = IntervalService.list("transactions")
    chart = []

    for interval in intervals:
        chart.append({
            "time": str(interval.time),
            "value": interval.value,
        })

    return utils.response(chart)

@blueprint.route("/latest", methods=["GET"])
@orm.db_session
def info():
    block = BlockService.latest_block()

    return utils.response({
        "time": block.created.timestamp(),
        "blockhash": block.blockhash,
        "height": block.height,
        "rewards": block.rewards
    })

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

@blueprint.route("/block/<string:bhash>/transactions", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def block_transactions(args, bhash):
    block = BlockService.get_by_hash(bhash)

    if block:
        transactions = block.transactions.page(args["page"])
        result = []

        for transaction in transactions:
            result.append(transaction.display())

        return utils.response(result)

    return utils.dead_response("Block not found"), 404
