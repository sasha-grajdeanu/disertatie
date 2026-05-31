def capped_countdown_sum(n, limit):
    total = 0
    i = 0

    while i < n:
        total = total + i
        if total > limit:
            total = limit
        i = i + 1

    return total
