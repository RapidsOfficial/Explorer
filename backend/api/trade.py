from backend.models.transaction import Transaction
from .args import offers_args, orders_args
from ..models import DexOffer, TradeOrder
from webargs.flaskparser import use_args
from flask import Blueprint
from pony import orm
from .. import utils

blueprint = Blueprint("trade", __name__, url_prefix="/v2/trade")

@blueprint.route("/offers", methods=["GET"])
@use_args(offers_args, location="query")
@orm.db_session
def dex_offers(args):
    result = []

    offers = DexOffer.select(
        lambda o: o.open == args["open"]
    )

    if args["ticker"]:
        offers = offers.filter(
            lambda o: o.currency == args["ticker"]
        )

        offers = offers.order_by(
            DexOffer.price, orm.desc(DexOffer.created)
        )
    else:
        offers = offers.order_by(
            orm.desc(DexOffer.created)
        )

    offers = offers.page(args["page"], pagesize=100)

    for offer in offers:
        result.append(offer.display)

    return utils.response(result)

@blueprint.route("/offer/<string:txid>", methods=["GET"])
@orm.db_session
def dex_offer(txid):
    if (transaction := Transaction.select(lambda t: t.txid == txid).first()):
        offer = DexOffer.get(transaction=transaction)

        return utils.response(offer.display)

    return utils.dead_response("Offer not found"), 404

@blueprint.route("/orders", methods=["GET"])
@use_args(orders_args, location="query")
@orm.db_session
def dex_orders(args):
    result = []

    orders = TradeOrder.select(
        lambda o: o.open == args["open"]
    )

    if args["ticker"]:
        orders = orders.filter(lambda o: o.currencyforsale == args["ticker"])

    if args["desired"]:
        orders = orders.filter(lambda o: o.currencydesired == args["desired"])

    orders = orders.order_by(
        orm.desc(TradeOrder.created)
    )

    orders = orders.page(args["page"], pagesize=100)

    for order in orders:
        result.append(order.display)

    return utils.response(result)

@blueprint.route("/order/<string:txid>", methods=["GET"])
@orm.db_session
def dex_order(txid):
    if (transaction := Transaction.select(lambda t: t.txid == txid).first()):
        order = TradeOrder.get(transaction=transaction)

        return utils.response(order.display)

    return utils.dead_response("Order not found"), 404
