# from backend import sync

# sync.sync_masternodes()
# sync.sync_blocks()
# sync.rollback_blocks(1630219)
from backend.models import Balance
from pony import orm

with orm.db_session:
    balances = Balance.select(lambda b: b.currency != "RPD")
    for balance in balances:
        balance.delete()
