from ..services import TransactionService
from flask import render_template
from pony import orm
from .. import utils
import math

def init(blueprint):
    @blueprint.route("/transactions", defaults={"page": 1})
    @blueprint.route("/transactions/<int:page>")
    @orm.db_session
    def transactions(page):
        size = 100

        transactions = TransactionService.transactions(page=page, size=size)
        count = TransactionService.count()
        total = math.ceil(count / size)

        pagination = utils.pagination(
            "frontend.transactions", page,
            size, total
        )

        return render_template(
            "pages/transactions.html", pagination=pagination,
            transactions=transactions
        )

    @blueprint.route("/transaction/<string:txid>")
    @orm.db_session
    def transaction(txid):
        if (transaction := TransactionService.get_by_txid(txid)):
            return render_template("pages/transaction.html", transaction=transaction)

        return render_template("pages/404.html")
