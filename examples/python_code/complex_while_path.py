def complex_while_path(n, limit):
    i = 0
    score = 0
    step = 1
    result = score

    while i < n and score <= limit:
        if i < 2:
            score = score + step + i
        else:
            if score + step > limit:
                score = score + 1
            else:
                score = score + step

        if score > limit:
            result = limit
        else:
            result = score

        i = i + 1
        step = step + 1

    return result
