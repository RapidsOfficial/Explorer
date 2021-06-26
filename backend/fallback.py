from .methods.transaction import Transaction
from datetime import datetime
from . import utils

def transaction(txid):
    data = Transaction.info(txid)
    if data["error"]:
        return None

    result = data["result"]
    amount = 0

    output_amount = 0
    input_amount = 0
    simple_vout = []
    tmp = {}

    for vout in result["vout"]:
        vout_amount = utils.amount(vout["value"])
        output_amount += vout_amount

        if vout["scriptPubKey"]["type"] != "nonstandard":
            address = vout["scriptPubKey"]["addresses"][0]
            if address not in tmp:
                tmp[address] = 0

            tmp[address] += vout_amount

    for address in tmp:
        simple_vout.append({
            "address": {
                "address": address
            },
            "amount": tmp[address]
        })

    simple_vin = []
    tmp = {}

    for vin in result["vin"]:
        vin_amount = utils.amount(vin["value"])
        input_amount += vin_amount

        if vin["scriptPubKey"]["type"] != "nonstandard":
            address = vin["scriptPubKey"]["addresses"][0]
            if address not in tmp:
                tmp[address] = 0

            tmp[address] += vin_amount

    for address in tmp:
        simple_vin.append({
            "address": {
                "address": address
            },
            "amount": tmp[address]
        })

    amount = output_amount
    fee = input_amount - output_amount

    simple_vout.reverse()
    simple_vin.reverse()

    transaction = {
        "txid": result["txid"],
        "size": result["size"],
        "block": None,
        "amount": amount,
        "fee": fee,
        "simple_vout": simple_vout,
        "simple_vin": simple_vin
    }

    if result["height"] != -1:
        transaction["block"] = {
            "created": datetime.fromtimestamp(result["time"]),
            "height": result["height"],
            "confirmations": result["confirmations"],
            "blockhash": result["blockhash"],
            "timestamp": result["time"]
        }

    return transaction
