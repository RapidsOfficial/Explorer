from webargs.flaskparser import use_args
from ..services import BlockService
from ..services import StatsService
from flask import redirect, url_for
from flask import render_template
from .args import search_args
from flask import Response
from pony import orm

def init(blueprint):
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

            elif len(args["query"]) == 34:
                return redirect(url_for("frontend.address", address=args["query"]))

        return redirect(url_for("frontend.home"))

    @blueprint.route("/docs")
    def docs():
        return render_template("pages/api.html")

    @blueprint.route("/ext/getmoneysupply")
    @orm.db_session
    def supply_info():
        supply = StatsService.get_by_key("supply")

        return Response(
            str(supply.value), mimetype="application/json"
        )
