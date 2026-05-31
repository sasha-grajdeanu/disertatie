def bonus_points(score, streak):
    if score >= 90 and streak > 3:
        return score + 10
    if score >= 70 or streak > 5:
        return score + 5
    return score
