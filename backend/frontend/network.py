from ..services import MasternodeService
from ..services import PeerService
from flask import render_template
from pony import orm
from .. import utils
import math

def init(blueprint):
    @blueprint.route("/network")
    @orm.db_session
    def network():
        peers = PeerService.list()

        title = "Network peers"

        return render_template(
            "pages/peers.html", peers=peers,
            title=title
        )

    @blueprint.route("/masternodes", defaults={"page": 1})
    @blueprint.route("/masternodes/<int:page>")
    @orm.db_session
    def masternodes(page):
        masternodes = MasternodeService.list()
        masternodes = masternodes.order_by(lambda m: m.rank)
        size = 100

        total = math.ceil(len(masternodes) / size)
        pagination = utils.pagination(
            "frontend.masternodes", page,
            size, total
        )

        masternodes = masternodes.page(page, pagesize=size)
        title = "Masternodes"

        return render_template(
            "pages/masternodes.html", masternodes=masternodes,
            pagination=pagination,
            title=title
        )
