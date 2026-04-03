'''
This is the module docstring.

There are some weird rules about how these have to look.
'''

from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo


now = datetime.now()
delta = timedelta(weeks=1)

no_way = now + delta
today = date.today()




utc_now = datetime.now(ZoneInfo("EST"))
print(utc_now)
eastern = datetime.now(ZoneInfo("America/New_York"))
converted = utc_now.astimezone(ZoneInfo("Europe/London"))

print(no_way)


# Create
dt = datetime(2025, 4, 4)
d = date(2025, 4, 3)
t = time(14, 30)

print(dt)
print(d)
print(t)



# Format to string
print(now.strftime("%Y-%m-%d %A %H:%M:%S"))    # "2025-04-03 14:30:00"
now.strftime("%B %d, %Y")            # "April 03, 2025"
