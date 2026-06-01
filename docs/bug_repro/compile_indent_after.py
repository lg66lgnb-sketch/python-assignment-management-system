def total_score(items):
    total = 0
    for item in items:
        total += item["score"]
    return total
