from ..services import TransactionService
from flask import render_template, request
from .. import fallback
from pony import orm
from .. import utils
import math

def init(blueprint):
    @blueprint.route("/transactions", defaults={"page": 1})
    @blueprint.route("/transactions/<int:page>")
    @orm.db_session
    def transactions(page):
        cookie = request.cookies.get("show-rewards")
        show = False

        if cookie == "true":
            show = True

        size = 100
        transactions = TransactionService.transactions(page=page, size=size, rewards=show)
        count = TransactionService.count(show)
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
        title = f"Transaction {txid[:16]}..."
        transaction = None

        if not (transaction := TransactionService.get_by_txid(txid)):
            transaction = fallback.transaction(txid)

        if transaction:
            return render_template(
                "pages/transaction.html",
                transaction=transaction,
                title=title
            )

        return render_template("pages/404.html")
