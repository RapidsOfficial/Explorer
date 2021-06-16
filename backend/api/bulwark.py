from webargs.flaskparser import use_args
from ..services import IntervalService
from ..services import BlockService
from flask import Blueprint
from .args import page_args
from .. import utils
from pony import orm

blueprint = Blueprint("bulwark", __name__, url_prefix="/api/")

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
