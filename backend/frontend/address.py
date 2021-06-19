from ..services import AddressService
from flask import render_template
from pony import orm
from .. import utils
import math

def init(blueprint):
    @blueprint.route("/address/<string:address>", defaults={"page": 1})
    @blueprint.route("/address/<string:address>/<int:page>")
    @orm.db_session
    def address(address, page):
        size = 10

        if (address := AddressService.get_by_address(address)):
            transactions = address.txs.page(page, pagesize=size)

            total = math.ceil(address.txcount / size)
            pagination = utils.pagination(
                "frontend.address", page,
                size, total
            )

            title = f"Address {address.address}"

            return render_template(
                "pages/address.html", address=address,
                transactions=transactions,
                pagination=pagination,
                title=title
            )

        return render_template("pages/404.html")

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

        title = "Top holders"

        return render_template(
            "pages/holders.html", richlist=richlist,
            pagination=pagination,
            title=title
        )
