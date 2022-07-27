from webargs.flaskparser import use_args
from flask import Blueprint

blueprint = Blueprint("dex", __name__, url_prefix="/v2/dex")

