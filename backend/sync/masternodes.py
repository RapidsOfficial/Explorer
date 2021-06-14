from ..services import MasternodeService
from datetime import datetime, timedelta
from ..methods.general import General
from ..services import AddressService
from .utils import log_message
from pony import orm

@orm.db_session
def sync_masternodes():
    masternodes = General.masternodes()

    if masternodes["error"] is None:
        total = len(masternodes["result"])

        log_message(f"Syncing {total} masternodes")

        knows_masternodes = MasternodeService.list()
        for masternode in knows_masternodes:
            masternode.activetime = timedelta(seconds=0)
            masternode.status = "DISABLED"
            masternode.active = False
            masternode.rank = None

        for masternode in masternodes["result"]:
            address = AddressService.get_by_address(masternode["addr"], True)
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

        # ToDo: masternodes historical data
