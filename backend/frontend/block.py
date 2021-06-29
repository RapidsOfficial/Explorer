from flask import render_template, redirect, url_for
from ..services import MasternodeService
from ..services import IntervalService
from ..services import AddressService
from ..services import BlockService
from ..services import StatsService
from pony import orm
from .. import utils
import math

def init(blueprint):
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

        chart = IntervalService.list("transactions")
        title = "Overview"

        non_reward_transactions = StatsService.get_by_key("non_reward_transactions")
        supply = StatsService.get_by_key("supply")
        masternodes = MasternodeService.total()
        collateral = 10000

        stats = {
            "addresses": AddressService.count(),
            "masternodes": masternodes,
            "transactions": int(non_reward_transactions.value),
            "collateral": collateral,
            "supply": round(supply.value, 2),
            "height": latest.height,
            "locked": collateral * masternodes
        }

        return render_template(
            "pages/overview.html", pagination=pagination,
            blocks=blocks, chart=chart,
            title=title, stats=stats
        )

    @blueprint.route("/block/<string:blockhash>", defaults={"page": 1})
    @blueprint.route("/block/<string:blockhash>/<int:page>")
    @orm.db_session
    def block(blockhash, page):
        size = 10

        if (block := BlockService.get_by_hash(blockhash)):
            transactions = block.txs.page(page, pagesize=size)

            total = math.ceil(block.txcount / size)
            pagination = utils.pagination(
                "frontend.block", page,
                size, total
            )

            title = f"Block #{block.height}"

            return render_template(
                "pages/block.html", block=block,
                transactions=transactions,
                pagination=pagination,
                title=title
            )

        return render_template("pages/404.html")

    @blueprint.route("/height/<int:height>")
    @orm.db_session
    def height(height):
        if (block := BlockService.get_by_height(height)):
            return redirect(url_for("frontend.block", blockhash=block.blockhash))

        return redirect(url_for("frontend.home"))
