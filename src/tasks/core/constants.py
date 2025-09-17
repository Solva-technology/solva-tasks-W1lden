from datetime import timedelta

ACCESS_TOKEN_EXPIRE = timedelta(hours=12)
LOG_FILE_PATH = "tasks/logs/app.log"
NOTIFY_INTERVAL = timedelta(minutes=15)
DEADLINE_GRACE = timedelta(minutes=0)
PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 200

DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 1800
