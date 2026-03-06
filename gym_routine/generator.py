from .state import get_exercise_weight
from .config import load_config
import requests
import json
import random
import logging

def generate_static_workout(day_index):
    config = load_config()
    exercises = config['routine']['exercises']
    duration = config['routine']['duration_minutes']

    # Define day splits
    day_splits = {
        0: {'focus': 'push', 'include': ['cardio']},  # Monday: Push + Cardio
        1: {'focus': 'pull', 'include': ['core']},    # Tuesday: Pull + Core
        2: {'focus': 'legs', 'include': ['explosive']},  # Wednesday: Legs + Explosive
        3: {'focus': 'explosive', 'include': ['cardio']},  # Thursday: Explosive + Cardio
        4: {'focus': 'mixed', 'include': ['push_pull']}  # Friday: Mixed + Complementary
    }

    split = day_splits[day_index]
    focus_exercises = [e for e in exercises if e['muscle_group'] == split['focus'] and not e['complementary']]
    include_exercises = []
    for inc in split['include']:
        include_exercises.extend([e for e in exercises if e['muscle_group'] == inc])

    # Select 2-3 focus exercises, rotate if possible
    selected_focus = random.sample(focus_exercises, min(3, len(focus_exercises)))
    selected_include = random.sample(include_exercises, min(2, len(include_exercises)))

    workout = []
    total_time = 0
    for ex in selected_focus + selected_include:
        weight_info = get_exercise_weight(ex['name'], ex['weight'])
        ex_copy = ex.copy()
        ex_copy['weight'] = weight_info['weight']
        ex_copy['reps'] = weight_info['reps'] or ex['reps']
        # Estimate time: sets * (reps * 5 sec + rest)
        time_est = ex['sets'] * (ex['reps'] * 5 + ex['rest_seconds'])
        ex_copy['time_estimate_seconds'] = time_est
        total_time += time_est
        workout.append(ex_copy)

    # Add stretch and abs if not present
    has_stretch = any('stretch' in ex['name'].lower() for ex in workout)
    has_abs = any('abs' in ex['name'].lower() or 'stomach' in ex['name'].lower() for ex in workout)
    if not has_stretch:
        workout.append({'name': 'Full Body Stretch', 'sets': 1, 'reps': 5, 'weight': 0, 'rest_seconds': 30, 'equipment': 'Bodyweight'})
    if not has_abs:
        workout.append({'name': 'Plank', 'sets': 3, 'reps': 30, 'weight': 0, 'rest_seconds': 30, 'equipment': 'Bodyweight'})

    return {
        'day': day_index,
        'exercises': workout,
        'total_time_estimate_minutes': round(total_time / 60, 1)
    }

def generate_workout(day_index):
    config = load_config()
    api_key = config.get('xai', {}).get('api_key', '')
    duration = config['routine']['duration_minutes']

    # Define day splits
    day_splits = {
        0: {'focus': 'push', 'include': ['cardio']},  # Monday: Push + Cardio
        1: {'focus': 'pull', 'include': ['core']},    # Tuesday: Pull + Core
        2: {'focus': 'legs', 'include': ['explosive']},  # Wednesday: Legs + Explosive
        3: {'focus': 'explosive', 'include': ['cardio']},  # Thursday: Explosive + Cardio
        4: {'focus': 'mixed', 'include': ['push_pull']}  # Friday: Mixed + Complementary
    }

    split = day_splits[day_index]

    # Prompt for XAI
    prompt = f"""
Generate a 40-minute calisthenics-style workout for {split['focus']} focus day, including {', '.join(split['include'])}.
Draw inspiration from the training styles of Instagram fitness influencers: @winnesworld, @cameronahouse, @jan.moves, @laget_om_ka, @juddiehard, @a_nagovicyn.
Incorporate elements like deadlifts, handstand push-ups, pull-ups, bench press, explosive moves (e.g., dumbbell squat to overhead press).
Always include a stretch section at the end and one abs/stomach focused exercise.

Available equipment (ONLY use exercises that can be performed with this equipment):
- Straight barbell
- Dumbbells: 20, 25, 30, 35, 40, 45, 50, 55 lbs (rubber plates available: 10, 15, 25, 45 lbs)
- Pull-up bar
- Bench
- Kettlebell: 25 lbs
- Kettlebell: 50 lbs
- Weighted vest: 10 lbs
- Bodyweight

For each exercise, specify which piece of equipment from the list above is used in the "equipment" field.
Output ONLY valid JSON in this exact format, no extra text:
{{"exercises": [{{"name": "Exercise Name", "sets": 3, "reps": 8, "weight": 0, "rest_seconds": 60, "equipment": "Equipment name"}}], "total_time_estimate_minutes": 40}}
"""

    # Call XAI API
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-4-latest",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"XAI API error: {response.text}")

        result = response.json()
        content = result['choices'][0]['message']['content']
        logging.info(f"LLM response: {content}")
        workout_data = json.loads(content)
    except Exception as e:
        logging.error(f"XAI API failed: {e}. Falling back to static generation.")
        return generate_static_workout(day_index)

    # Apply current weights
    for ex in workout_data['exercises']:
        weight_info = get_exercise_weight(ex['name'], ex.get('weight', 0))
        ex['weight'] = weight_info['weight']
        ex['reps'] = weight_info['reps'] or ex['reps']

    return {
        'day': day_index,
        'exercises': workout_data['exercises'],
        'total_time_estimate_minutes': workout_data.get('total_time_estimate_minutes', duration)
    }