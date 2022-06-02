from ..methods.general import General
from ..services import PeerService
from .utils import log_message
from pony import orm
from .. import utils

@orm.db_session(serializable=True)
def sync_peers():
    peers = General.peers()

    if peers["error"] is None:
        total = len(peers["result"])

        log_message(f"Syncing {total} peers")

        knows_peers = PeerService.list(True)
        for peer in knows_peers:
            peer.active = False

        for peer in peers["result"]:
            address, port = peer["addr"].split(":")
            version = peer["version"]
            subver = peer["subver"]

            if address[0] == "[":
                continue

            if not subver:
                continue

            if (known_peer := PeerService.get_by_address(address)):
                known_peer.active = True

            else:
                known_peer = PeerService.create(address, port, version, subver)

            if not known_peer.location:
                if (location := utils.location(address)):
                    PeerService.location(
                        location["country"], location["lat"],
                        location["lon"], location["city"],
                        location["code"], known_peer
                    )

        # ToDo: peer historical data
