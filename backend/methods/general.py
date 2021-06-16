from .. import utils

class General():
    @classmethod
    def info(cls):
        data = utils.make_request("getblockchaininfo")

        if data["error"] is None:
            mempool = cls.mempool()["result"]["size"]

            data["result"]["mempool"] = mempool
            data["result"]["reward"] = utils.reward(data["result"]["blocks"])
            data["result"].pop("verificationprogress")
            data["result"].pop("pruned")
            data["result"].pop("softforks")
            data["result"].pop("bip9_softforks")
            data["result"].pop("warnings")
            data["result"].pop("size_on_disk")

            nethash = utils.make_request("getnetworkhashps", [120, data["result"]["blocks"]])
            if nethash["error"] is None:
                data["result"]["nethash"] = int(nethash["result"])

        return data

    @classmethod
    def fee(cls):
        data = utils.make_request("estimatesmartfee", [6])

        if data["error"] is None:
            data["result"]["feerate"] = utils.satoshis(data["result"]["feerate"])
        else:
            data = utils.response({
                "feerate": utils.satoshis(0.001),
                "blocks": 6
            })

        return data

    @classmethod
    def mempool(cls):
        data = utils.make_request("getmempoolinfo")

        if data["error"] is None:
            if data["result"]["size"] > 0:
                mempool = utils.make_request("getrawmempool")["result"]
                data["result"]["tx"] = mempool
            else:
                data["result"]["tx"] = []

        return data

    @classmethod
    def current_height(cls):
        data = utils.make_request("getblockcount")
        height = 0

        if data["error"] is None:
            height = data["result"]

        return height

    @classmethod
    def masternodes(cls):
        data = utils.make_request("listmasternodes")
        return data

    @classmethod
    def peers(cls):
        data = utils.make_request("getpeerinfo")
        return data

    @classmethod
    def getdifficulty(cls):
        data = utils.make_request("getdifficulty")
        return data
