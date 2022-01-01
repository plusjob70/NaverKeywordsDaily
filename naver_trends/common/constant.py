from datetime import datetime

PC = 0
MO = 1

ID      = 0
SECRET  = 1
LICENSE = 2

IS_DANGEROUS_TIME   = '00:00' < datetime.now().strftime('%H:%M') < '10:30'
DEFAULT_LATEST_DATE = '2015-12-31'
START_DATE          = datetime(2016, 1, 1).date()
DAY_DIFF            = (datetime.now() - datetime(2016, 1, 1, 10, 30, 0)).days