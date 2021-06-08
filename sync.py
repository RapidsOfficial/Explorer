from apscheduler.schedulers.blocking import BlockingScheduler
from backend import sync

background = BlockingScheduler()
background.add_job(sync.sync_blocks, "interval", seconds=5)
background.start()
