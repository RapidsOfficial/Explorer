from ..methods.transaction import Transaction
from .. import utils

class Block():
    @classmethod
    def raw(cls, block_hash):
        raw_block = utils.make_request("getblock", [block_hash, False])["result"]

        return raw_block

    @classmethod
    def height(cls, height: int):
        data = utils.make_request("getblockhash", [height])

        if data["error"] is None:
            txid = data["result"]
            data.pop("result")
            data["result"] = utils.make_request("getblock", [txid])["result"]
            data["result"]["stake"] = "stakeModifier" in data["result"]
            data["result"]["txcount"] = len(data["result"]["tx"])
            reward = 0

            if data["result"]["height"] != 0:
                if data["result"]["stake"]:
                    tx = Transaction.info(data["result"]["tx"][1])
                    outputs = 0
                    inputs = 0

                    for vin in tx["result"]["vin"]:
                        inputs += vin["value"]

                    for vout in tx["result"]["vout"]:
                        outputs += vout["value"]

                    reward = outputs - inputs

                else:
                    tx = Transaction.info(data["result"]["tx"][0])
                    reward = tx["result"]["vout"][0]["value"]

            data["result"]["reward"] = reward

        return data

    @classmethod
    def hash(cls, bhash: str):
        data = utils.make_request("getblock", [bhash])

        if data["error"] is None:
            data["result"]["txcount"] = len(data["result"]["tx"])
            data["result"]["stake"] = "stakeModifier" in data["result"]
            reward = 0

            if data["result"]["height"] != 0:
                if data["result"]["stake"]:
                    tx = Transaction.info(data["result"]["tx"][1])
                    outputs = 0
                    inputs = 0

                    for vin in tx["result"]["vin"]:
                        inputs += vin["value"]

                    for vout in tx["result"]["vout"]:
                        outputs += vout["value"]

                    reward = outputs - inputs

                else:
                    tx = Transaction.info(data["result"]["tx"][0])
                    reward = tx["result"]["vout"][0]["value"]

            data["result"]["reward"] = reward

        return data

    @classmethod
    def get(cls, height: int):
        return utils.make_request("getblockhash", [height])

    @classmethod
    def range(cls, height: int, offset: int):
        result = []
        for block in range(height - (offset - 1), height + 1):
            data = utils.make_request("getblockhash", [block])
            nethash = utils.make_request("getnetworkhashps", [120, block])

            if data["error"] is None and nethash["error"] is None:
                txid = data["result"]
                data.pop("result")
                data["result"] = utils.make_request("getblock", [txid])["result"]
                data["result"]["txcount"] = len(data["result"]["tx"])
                data["result"]["nethash"] = int(nethash["result"])

                result.append(data["result"])

        return result[::-1]

    @classmethod
    def chart(cls):
        def chunks(data, n):
            n = max(1, n)
            return (data[i:i + n] for i in range(0, len(data), n))

        data = utils.make_request("getblockchaininfo")
        height = data["result"]["blocks"]
        offset = 1440
        result = []

        for chunk in chunks(range(height - (offset - 1), height + 1), 24):
            height = chunk[0]
            total = 0

            for block in chunk:
                data = utils.make_request("getblockhash", [block])

                if data["error"] is None:
                    tx_data = utils.make_request("getblock", [data["result"]])["result"]
                    total += len(tx_data["tx"])

            result.append([height, total])

        return result

    @classmethod
    def inputs(cls, bhash: str):
        data = cls.hash(bhash)
        return Transaction().addresses(data["result"]["tx"])

    @classmethod
    def blockhash(cls, height: int):
        data = utils.make_request("getblockhash", [height])
        return data["result"]

    @classmethod
    def header(cls, bhash: str):
        return utils.make_request("getblockheader", [bhash])
