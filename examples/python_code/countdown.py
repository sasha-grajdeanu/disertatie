def countdown(n, start):
    total = start
    while n > 0:
        total = total - n
        n = n - 1
    return total
