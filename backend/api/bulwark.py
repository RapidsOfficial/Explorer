from ..services import TransactionService
from ..services import MasternodeService
from webargs.flaskparser import use_args
from ..services import AddressService
from ..services import BalanceService
from ..services import BlockService
from ..services import StatsService
from ..services import PeerService
from ..constants import CURRENCY
from flask import Blueprint
from flask import Response
from pony.orm import desc
from pony import orm
import json

from ..methods.transaction import Transaction
from ..methods.general import General
from .args import bulwark_broadcast_args

# This blueprint is intended for partial backward compatibility with Bulwark explorer.
# Do not add new API calls here! Do that in v2 blueprint.

blueprint = Blueprint("bulwark", __name__, url_prefix="/api/")

@blueprint.route("/sendrawtransaction", methods=["POST"])
@use_args(bulwark_broadcast_args, location="form")
def broadcast(args):
    data = Transaction.broadcast(args["rawtx"])

    if data["error"]:
        return {"error": json.dumps(data["error"])}

    return {"raw": data["result"]}

@blueprint.route("/login", methods=["POST"])
def login():
    return "Not implemented"

@blueprint.route("/address/<string:raw_address>", methods=["GET"])
@orm.db_session
def address(raw_address):
    if (address := AddressService.get_by_address(raw_address)):
        balance = BalanceService.get_by_currency(address, CURRENCY)
        first_transaction = address.transactions.order_by(
            lambda t: t.block.created
        ).first()

        latest_transaction = address.transactions.order_by(
            lambda t: desc(t.block.created)
        ).first()

        masternode = False

        if MasternodeService.get_by_address(raw_address):
            masternode = True

        return {
            "label": address.address,
            "balance": balance.balance,
            "blockHeight": first_transaction.block.height,
            "date": first_transaction.block.created.isoformat(),
            "lastMovementDate": latest_transaction.block.created.isoformat(),
            "lastMovementBlockHeight": latest_transaction.block.height,
            "valueIn": balance.received,
            "isMasternode": masternode,
            "valueOut": balance.sent
        }

    return "Address Not Found"

@blueprint.route("/block/<string:blockhash>", methods=["GET"])
@orm.db_session
def block(blockhash):
    if (block := BlockService.get_by_hash(blockhash)):
        prev = block.previous_block
        transactions = []

        for transaction in block.txs:
            transactions.append({
                "txId": transaction.txid,
                "blockHeight": transaction.block.height,
                "date": transaction.block.created.isoformat(),
                "isReward": transaction.is_reward,
                "addressesIn": transaction.input_amount,
                "addressesOut": transaction.output_amount,
            })

        return {
            "hash": block.blockhash,
            "height": block.height,
            "confirmations": block.confirmations,
            "createdAt": block.created.isoformat(),
            "bits": hex(block.bits)[2:],
            "merkle": block.merkleroot,
            "nonce": block.nonce,
            "prev": prev.blockhash if prev else None,
            "size": block.size,
            "ver": block.version,
            "isConfirmed": True,
            "txs": transactions
        }

    return "Unable to find the block!"

@blueprint.route("/block/<int:height>", methods=["GET"])
@orm.db_session
def block_height(height):
    if (block := BlockService.get_by_height(height)):
        prev = block.previous_block
        transactions = []

        for transaction in block.txs:
            transactions.append({
                "txId": transaction.txid,
                "blockHeight": transaction.block.height,
                "date": transaction.block.created.isoformat(),
                "isReward": transaction.is_reward,
                "addressesIn": transaction.input_amount,
                "addressesOut": transaction.output_amount,
            })

        return {
            "hash": block.blockhash,
            "height": block.height,
            "confirmations": block.confirmations,
            "createdAt": block.created.isoformat(),
            "bits": hex(block.bits)[2:],
            "merkle": block.merkleroot,
            "nonce": block.nonce,
            "prev": prev.blockhash if prev else None,
            "size": block.size,
            "ver": block.version,
            "isConfirmed": True,
            "txs": transactions
        }

    return "Unable to find the block!"

@blueprint.route("/block/average", methods=["GET"])
def block_average():
    return "Not implemented"

@blueprint.route("/coin", methods=["GET"])
def coin_info():
    return "Not implemented"

@blueprint.route("/history", methods=["GET"])
def coin_history():
    return "Not implemented"

@blueprint.route("/masternode", methods=["GET"])
def masternodes_list():
    return "Not implemented"

@blueprint.route("/masternode/<string:raw_address>", methods=["GET"])
def address_masternodes(raw_address):
    return "Not implemented"

@blueprint.route("/masternodecount", methods=["GET"])
@orm.db_session
def masternodes_count():
    return {
        "enabled": MasternodeService.enabled(),
        "total": MasternodeService.total()
    }

@blueprint.route("/masternode/average", methods=["GET"])
def masternode_average():
    return "Not implemented"

@blueprint.route("/peer", methods=["GET"])
@orm.db_session
def peers():
    peers = PeerService.list()
    result = []

    for peer in peers:
        result.append({
            "country": peer.location.country,
            "createdAt": peer.created.isoformat(),
            "lat": peer.location.lat,
            "lon": peer.location.lon,
            "port": peer.port,
            "subver": peer.subver,
            "ver": peer.version
        })

    return Response(
        json.dumps(result), mimetype="application/json"
    )

@blueprint.route("/supply", methods=["GET"])
@orm.db_session
def supply():
    supply = StatsService.get_by_key("supply")

    return {
        "c": supply.value,
        "t": supply.value
    }

@blueprint.route("/getmapdata", methods=["GET"])
def map_data():
    return "Not implemented"

@blueprint.route("/top100", methods=["GET"])
def richlist():
    return "Not implemented"

@blueprint.route("/tx", methods=["GET"])
def transactions_list():
    return "Not implemented"

@blueprint.route("/rewards", methods=["GET"])
def rewards():
    return "Not implemented"

@blueprint.route("/tx/latest", methods=["GET"])
@orm.db_session
def latest_transactions():
    transactions = TransactionService.transactions(page=1, size=10)
    result = []

    for transaction in transactions:
        result.append({
            "txId": transaction.txid,
            "blockHeight": transaction.block.height,
            "date": transaction.block.created.isoformat(),
            "isReward": transaction.is_reward,
            "addressesIn": transaction.input_amount,
            "addressesOut": transaction.output_amount,
        })

    return Response(
        json.dumps(result), mimetype="application/json"
    )

@blueprint.route("/tx/<string:txid>", methods=["GET"])
@orm.db_session
def transaction(txid):
    if (transaction := TransactionService.get_by_txid(txid)):
        return {
            "txId": transaction.txid,
            "blockHeight": transaction.block.height,
            "date": transaction.block.created.isoformat(),
            "isReward": transaction.is_reward,
            "addressesIn": transaction.input_amount,
            "addressesOut": transaction.output_amount,
        }

    return "Unable to find the transaction!"

@blueprint.route("/getdifficulty", methods=["GET"])
@orm.db_session
def difficulty():
    data = General.getdifficulty()
    result = 0

    if not data["error"]:
        result = data["result"]

    return Response(
        str(result), mimetype="application/json"
    )

@blueprint.route("/getblockcount", methods=["GET"])
@orm.db_session
def block_count():
    count = 1

    if (block := BlockService.latest_block()):
        count += block.height

    return Response(
        str(count), mimetype="application/json"
    )

@blueprint.route("/getnetworkhashps", methods=["GET"])
def network_hashrate():
    return "Not implemented"

@blueprint.route("/movements", methods=["GET"])
def movements():
    return "Not implemented"

@blueprint.route("/timeIntervals", methods=["GET"])
def time_intervals():
    return "Not implemented"
