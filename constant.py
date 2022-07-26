# 10 min, 1 hour, 12 hours, 1 day, 3 days, 1 week, 3 weeks
MIN = 60
HOUR = 60 * MIN
DAY = 24 * HOUR
WEEK = 7 * DAY

NEXT_RECALL_STR = ["10 Minutes", "1 Hour", "12 Hours", "1 Day", "3 Days", "1 Week", "3 Weeks"]

NEXT_RECALL = [
    10 * MIN, HOUR, 12 * HOUR, DAY, 3 * DAY, WEEK, 3* WEEK
]

VIEW_RANGE = DAY