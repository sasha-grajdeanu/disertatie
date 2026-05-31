def risky_running_average(n, total, count):
    i = 0
    acc = total

    while i < n:
        if i < 2:
            acc = acc + i + 1
        else:
            acc = acc + 2
        i = i + 1

    if acc > 10:
        divisor = count - n
    else:
        divisor = count

    return int(acc / divisor)
