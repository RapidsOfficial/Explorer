from .deserializer import Deserializer
from .hash import hash_to_hex_str
from . import script
import struct

def read_header(block, length=80):
    header = struct.Struct('< I 32s 32s I I I').unpack_from(block[:length])

    return {
        "stake": False,
        "version": header[0],
        "prev": hash_to_hex_str(header[1]),
        "merkle": hash_to_hex_str(header[2]),
        "timestamp": header[3],
        "bits": header[4],
        "nonce": header[5],
        "size": len(block)
    }

def read_tx(block):
    txs = Deserializer(block, start=80).read_tx_block()
    result = []

    for tx_index, tx in enumerate(txs):
        raw = tx[0].serialize()
        outputs = []
        inputs = []

        for vin in tx[0].inputs:
            inputs.append({
                "coinbase": vin.is_generation(),
                "txid": hash_to_hex_str(vin.prev_hash),
                "script": vin.script.hex(),
                "sequence": vin.sequence,
                "vout": vin.prev_idx
            })

        for index, vout in enumerate(tx[0].outputs):
            script_type, address = script.script_type(vout.pk_script)

            outputs.append({
                "value": vout.value,
                "script": vout.pk_script.hex(),
                "type": script_type,
                "address": address,
                "n": index
            })

        result.append({
            "txid": hash_to_hex_str(tx[1]),
            "version": tx[0].version,
            "locktime": tx[0].locktime,
            "size": len(raw),
            "hex": raw.hex(),
            "index": tx_index,
            "outputs": outputs,
            "inputs": inputs
        })

    return result

def process(raw_block):
    block = bytes.fromhex(raw_block)

    header = read_header(block)
    txs = read_tx(block)

    if len(txs) > 1:
        if len(txs[1]["inputs"]) > 0 and len(txs[1]["outputs"]) >= 2:
            if txs[1]["outputs"][0]["type"] is None:
                header["stake"] = True

    return header, txs
