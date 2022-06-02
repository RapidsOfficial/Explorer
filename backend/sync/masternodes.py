from ..services import MasternodeService
from ..services import IntervalService
from ..methods.general import General
from .utils import log_message
from datetime import datetime
from pony import orm
from . import utils

@orm.db_session(serializable=True)
def sync_masternodes():
    INTERVAL_KEY = "masternodes"

    masternodes = General.masternodes()

    if masternodes["error"] is None:
        total = len(masternodes["result"])

        log_message(f"Syncing {total} masternodes")

        knows_masternodes = MasternodeService.list(True)
        for masternode in knows_masternodes:
            masternode.status = "DISABLED"
            masternode.activetime = 0
            masternode.active = False
            masternode.rank = None

        for masternode in masternodes["result"]:
            lastseen = datetime.fromtimestamp(masternode["lastseen"])
            lastpaid = datetime.fromtimestamp(masternode["lastpaid"])
            activetime = masternode["activetime"]
            version = masternode["version"]
            txhash = masternode["txhash"]
            outidx = masternode["outidx"]
            status = masternode["status"]
            pubkey = masternode["pubkey"]
            address = masternode["addr"]
            rank = masternode["rank"]

            if (knows_masternode := MasternodeService.get_by_address(address)):
                knows_masternode.activetime = activetime
                knows_masternode.lastseen = lastseen
                knows_masternode.lastpaid = lastpaid
                knows_masternode.version = version
                knows_masternode.txhash = txhash
                knows_masternode.outidx = outidx
                knows_masternode.status = status
                knows_masternode.pubkey = pubkey
                knows_masternode.active = True
                knows_masternode.rank = rank

            else:
                MasternodeService.create(
                    rank, activetime, lastseen, lastpaid,
                    version, address, txhash, outidx,
                    status, pubkey
                )

        time = utils.datetime_round_day(datetime.utcnow())
        interval = IntervalService.get_by_time(INTERVAL_KEY, time)

        if not interval:
            interval = IntervalService.create(INTERVAL_KEY, time)

        interval.value = total
