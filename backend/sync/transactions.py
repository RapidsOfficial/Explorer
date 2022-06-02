from ..services import IntervalService
from ..services import BlockService
from datetime import timedelta
from .utils import log_message
from pony import orm
from . import utils

@orm.db_session(serializable=True)
def sync_transactions():
    INTERVAL_KEY = "transactions"

    latest_inteval = IntervalService.latest(INTERVAL_KEY)

    if not latest_inteval:
        genesis = BlockService.get_by_height(0)

        if not genesis:
            return False

        timestamp = utils.datetime_round_day(genesis.created)

        latest_inteval = IntervalService.create(
            INTERVAL_KEY, timestamp
        )

    start = latest_inteval.time

    while True:
        end = start + timedelta(days=1)
        total = 0

        blocks = BlockService.time_range(start, end)

        for block in blocks:
            reward_tx = 0 if block.height == 0 else 1
            total += block.txcount - reward_tx

        log_message(f"Transaction chart: total {total} transactions in {blocks.count()} blocks")

        latest_inteval.value = total

        if BlockService.time_range(end, None).count() == 0:
            break

        start = end
        latest_inteval = IntervalService.create(
            INTERVAL_KEY, start
        )
