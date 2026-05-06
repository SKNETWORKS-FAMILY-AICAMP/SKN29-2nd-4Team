from datetime import datetime, date

def make_datetime(d: date, hour: int, minute: int) -> datetime:
    return datetime(
        year=d.year,
        month=d.month,
        day=d.day,
        hour=hour,
        minute=minute,
        second=0
    )