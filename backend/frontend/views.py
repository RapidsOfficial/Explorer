from flask import Blueprint
from . import transaction
from . import address
from . import general
from . import network
from . import block

blueprint = Blueprint("frontend", __name__)

transaction.init(blueprint)
address.init(blueprint)
general.init(blueprint)
network.init(blueprint)
block.init(blueprint)
