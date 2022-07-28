from .args import managed_args, crowdsale_args
from webargs.flaskparser import use_args
from .args import trade_cancel_pair_args
from .args import send_args, fixed_args
from .args import multisig_args
from .args import dex_sell_args
from .args import trade_args
from .args import close_args
from flask import Blueprint
from .. import utils
from pony import orm

blueprint = Blueprint("payload", __name__, url_prefix="/v2/payload/")

@blueprint.route("/send", methods=["POST"])
@use_args(send_args, location="json")
@orm.db_session
def payload_send(args):
    return utils.make_request(
        "createtokenpayloadsimplesend", [
            args["ticker"], str(args["amount"])
        ]
    )

@blueprint.route("/create/fixed", methods=["POST"])
@use_args(fixed_args, location="json")
@orm.db_session
def payload_create_fixed(args):
    token_type = 1 if not args["divisible"] else 2
    return utils.make_request(
        "createtokenpayloadissuancefixed", [
            1, token_type, 0, args["category"], args["subcategory"],
            args["name"], args["ticker"], args["url"], args["data"],
            str(args["amount"])
        ]
    )

@blueprint.route("/create/managed", methods=["POST"])
@use_args(managed_args, location="json")
@orm.db_session
def payload_create_managed(args):
    token_type = 1 if not args["divisible"] else 2
    return utils.make_request(
        "createtokenpayloadissuancemanaged", [
            1, token_type, 0, args["category"], args["subcategory"],
            args["name"], args["ticker"], args["url"], args["data"]
        ]
    )

@blueprint.route("/create/crowdsale", methods=["POST"])
@use_args(crowdsale_args, location="json")
@orm.db_session
def payload_create_crowdsale(args):
    token_type = 1 if not args["divisible"] else 2
    return utils.make_request(
        "createtokenpayloadissuancecrowdsale", [
            1, token_type, 0, args["category"], args["subcategory"],
            args["name"], args["ticker"], args["url"], args["data"],
            str(args["tokensperunit"]), args["deadline"], args["earlybonus"],
            args["issuerpercentage"]
        ]
    )

@blueprint.route("/crowdsale/close", methods=["POST"])
@use_args(close_args, location="json")
@orm.db_session
def payload_close_crowdsale(args):
    return utils.make_request(
        "createtokenpayloadclosecrowdsale", [
            args["ticker"]
        ]
    )

@blueprint.route("/managed/grant", methods=["POST"])
@use_args(send_args, location="json")
@orm.db_session
def payload_grant_managed(args):
    return utils.make_request(
        "createtokenpayloadgrant", [
            args["ticker"], str(args["amount"])
        ]
    )

@blueprint.route("/managed/revoke", methods=["POST"])
@use_args(send_args, location="json")
@orm.db_session
def payload_revoke_managed(args):
    return utils.make_request(
        "createtokenpayloadrevoke", [
            args["ticker"], str(args["amount"])
        ]
    )

@blueprint.route("/multisig", methods=["POST"])
@use_args(multisig_args, location="json")
@orm.db_session
def payload_multisig(args):
    return utils.make_request(
        "createrawtokentxmultisig", [
            "", args["payload"],
            args["address"],
            args["pubkey"]
        ]
    )

@blueprint.route("/dex/sell", methods=["POST"])
@use_args(dex_sell_args, location="json")
@orm.db_session
def payload_dex_send(args):
    action = ["new", "update", "cancel"].index(args["action"]) + 1

    return utils.make_request(
        "createtokenpayloaddexsell", [
            args["ticker"], str(args["amountforsale"]),
            str(args["amountdesired"]), args["paymentwindow"],
            str(args["minacceptfee"]), action
        ]
    )

@blueprint.route("/dex/accept", methods=["POST"])
@use_args(send_args, location="json")
@orm.db_session
def payload_dex_accept(args):
    return utils.make_request(
        "createtokenpayloaddexaccept", [
            args["ticker"], str(args["amount"])
        ]
    )

@blueprint.route("/trade/create", methods=["POST"])
@use_args(trade_args, location="json")
@orm.db_session
def payload_trade_create(args):
    return utils.make_request(
        "createtokenpayloadtrade", [
            args["tickerforsale"], str(args["amountforsale"]),
            args["tickerdesired"], str(args["amountdesired"])
        ]
    )

@blueprint.route("/trade/cancel/price", methods=["POST"])
@use_args(trade_args, location="json")
@orm.db_session
def payload_trade_cancel_price(args):
    return utils.make_request(
        "createtokenpayloadcanceltradesbyprice", [
            args["tickerforsale"], str(args["amountforsale"]),
            args["tickerdesired"], str(args["amountdesired"])
        ]
    )

@blueprint.route("/trade/cancel/pair", methods=["POST"])
@use_args(trade_cancel_pair_args, location="json")
@orm.db_session
def payload_trade_cancel_pair(args):
    return utils.make_request(
        "createtokenpayloadcanceltradesbypair", [
            args["tickerforsale"], args["tickerdesired"]
        ]
    )

@blueprint.route("/trade/cancel/all", methods=["POST"])
@orm.db_session
def payload_trade_cancel_all():
    return utils.make_request(
        "createtokenpayloadcancelalltrades", [1]
    )

