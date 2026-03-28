

def get_time(start,finish):
    total_seconds = finish-start
    if total_seconds > 60:
        min , sec = divmod(total_seconds,60)
        return min,sec
    return total_seconds