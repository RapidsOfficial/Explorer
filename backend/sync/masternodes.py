from ..services import MasternodeService
from datetime import datetime, timedelta
from ..services import IntervalService
from ..methods.general import General
from ..services import AddressService
from .utils import log_message
from pony import orm
from . import utils

@orm.db_session
def sync_masternodes():
    INTERVAL_KEY = "masternodes"

    masternodes = General.masternodes()

    if masternodes["error"] is None:
        total = len(masternodes["result"])
        now = datetime.utcnow()

        log_message(f"Syncing {total} masternodes")

        knows_masternodes = MasternodeService.list()
        for masternode in knows_masternodes:
            masternode.activetime = timedelta(seconds=0)
            masternode.status = "DISABLED"
            masternode.active = False
            masternode.rank = None

        for masternode in masternodes["result"]:
            address = AddressService.get_by_address(masternode["addr"], True, now)
            lastseen = datetime.fromtimestamp(masternode["lastseen"])
            lastpaid = datetime.fromtimestamp(masternode["lastpaid"])
            activetime = timedelta(seconds=masternode["activetime"])
            version = masternode["version"]
            txhash = masternode["txhash"]
            outidx = masternode["outidx"]
            status = masternode["status"]
            pubkey = masternode["pubkey"]
            rank = masternode["rank"]

            if (knows_masternode := MasternodeService.get_by_address(address)):
                knows_masternode.activetime = activetime
                knows_masternode.status = status
                knows_masternode.active = True
                knows_masternode.rank = rank

            else:
                MasternodeService.create(
                    rank, activetime, lastseen, lastpaid,
                    version, address, txhash, outidx,
                    status, pubkey
                )

        time = utils.datetime_round_minute5(now)
        interval = IntervalService.get_by_time(INTERVAL_KEY, time)

        if not interval:
            interval = IntervalService.create(INTERVAL_KEY, time)

        interval.value = total
