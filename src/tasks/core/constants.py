from datetime import timedelta

ACCESS_TOKEN_EXPIRE = timedelta(hours=12)
LOG_FILE_PATH = "tasks/logs/app.log"
NOTIFY_INTERVAL = timedelta(days=1)
DEADLINE_GRACE = timedelta(minutes=0)
PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 200
