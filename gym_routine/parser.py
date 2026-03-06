import re

def parse_adjustments(text):
    adjustments = []
    # Patterns for adjustments
    increase_pattern = re.findall(r'increase\s+(\w+(?:\s+\w+)*)\s+to\s+(\d+)', text, re.IGNORECASE)
    for match in increase_pattern:
        exercise = match[0].strip()
        weight = int(match[1])
        adjustments.append({'exercise': exercise, 'weight': weight, 'reps': None})

    reps_pattern = re.findall(r'did\s+(\d+)\s+reps\s+on\s+([a-zA-Z\s-]+)', text, re.IGNORECASE)
    for match in reps_pattern:
        reps = int(match[0])
        exercise = match[1].strip()
        adjustments.append({'exercise': exercise, 'weight': None, 'reps': reps})

    # More patterns can be added
    return adjustments