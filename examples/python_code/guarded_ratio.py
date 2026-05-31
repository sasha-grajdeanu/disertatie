def guarded_ratio(total, count, limit):
    if count <= 0:
        return 0

    adjusted = total
    if adjusted < 0:
        adjusted = 0

    ratio = adjusted // count
    if ratio > limit:
        return limit
    return ratio
