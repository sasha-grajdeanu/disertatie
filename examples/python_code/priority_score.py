def priority_score(age, income, flags):
    score = 0

    if age < 18:
        score = score - 5
    else:
        if income > 5000 and flags > 0:
            score = score + 10
        else:
            if income > 3000 or flags > 2:
                score = score + 5
            else:
                score = score + 1

    if score < 0:
        return 0
    return score
