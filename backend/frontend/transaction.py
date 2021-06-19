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

        title = "Recent transactions"

        return render_template(
            "pages/transactions.html", pagination=pagination,
            transactions=transactions,
            title=title
        )

    @blueprint.route("/transaction/<string:txid>")
    @orm.db_session
    def transaction(txid):
        # ToDo: Add fallback request to node in case if transaction is in mempool
        if (transaction := TransactionService.get_by_txid(txid)):
            title = f"Transaction {transaction.txid[:16]}..."

            return render_template(
                "pages/transaction.html",
                transaction=transaction,
                title=title
            )

        return render_template("pages/404.html")
