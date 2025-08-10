# app/utils/shift.py
from datetime import datetime, time

def is_within_shift(shift: str, current_time=None) -> bool:
    now = current_time or datetime.now().time()

    if shift == "A":
        return time(6, 0) <= now <= time(13, 59)
    elif shift == "B":
        return time(14, 0) <= now <= time(21, 59)
    elif shift == "C":
        return now >= time(22, 0) or now <= time(5, 59)
    return False
