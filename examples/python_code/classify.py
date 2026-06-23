def classify(score):
    if score >= 60:
        return 1
    else:
        if score >= 80:
            return 2
        else:
            return 0
