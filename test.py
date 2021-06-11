from backend.services import TransactionService
from datetime import datetime
from pony import orm

with orm.db_session(sql_debug=True):
    start = datetime.now()
    TransactionService.count()
    print(datetime.now() - start)
