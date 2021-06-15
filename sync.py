from apscheduler.schedulers.blocking import BlockingScheduler
from backend import sync

background = BlockingScheduler()
background.add_job(sync.sync_transactions, "interval", minutes=1)
background.add_job(sync.sync_masternodes, "interval", minutes=1)
background.add_job(sync.sync_blocks, "interval", seconds=30)
background.add_job(sync.sync_peers, "interval", minutes=1)
background.start()
