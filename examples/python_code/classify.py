def classify(x, y):
    if x + y > 10:
        if x + y < 5:
            return -1
        else:
            return 1
    else:
        return 0
