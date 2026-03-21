from .state import get_exercise_weight
from .config import load_config
import requests
import json
import random
import logging

logger = logging.getLogger(__name__)

# Day split definitions
DAY_SPLITS = {
    0: {'focus': 'push', 'include': ['cardio'], 'name': 'Push + Cardio'},
    1: {'focus': 'pull', 'include': ['core'], 'name': 'Pull + Core'},
    2: {'focus': 'legs', 'include': ['explosive'], 'name': 'Legs + Explosive'},
    3: {'focus': 'explosive', 'include': ['cardio'], 'name': 'Explosive + Cardio'},
    4: {'focus': 'mixed', 'include': ['push_pull'], 'name': 'Mixed + Complementary'}
}


def _build_equipment_list(config):
    """Build a readable equipment list from config."""
    lines = []
    for eq in config.get('equipment', []):
        line = f"- {eq['name']}"
        if 'available_weights_lbs' in eq:
            line += f": {', '.join(str(w) for w in eq['available_weights_lbs'])} lbs"
        if 'notes' in eq:
            line += f" ({eq['notes']})"
        lines.append(line)
    return '\n'.join(lines)


def _strip_markdown_fences(content):
    """Strip markdown code fences that LLMs often wrap JSON in."""
    content = content.strip()
    if content.startswith('```'):
        # Remove first line (```json or ```)
        content = content.split('\n', 1)[1] if '\n' in content else content[3:]
        # Remove trailing fence
        if '```' in content:
            content = content.rsplit('```', 1)[0]
    return content.strip()


def generate_static_workout(day_index):
    config = load_config()
    exercises = config['routine']['exercises']

    split = DAY_SPLITS[day_index]
    focus_exercises = [e for e in exercises if e['muscle_group'] == split['focus'] and not e['complementary']]
    include_exercises = []
    for inc in split['include']:
        include_exercises.extend([e for e in exercises if e['muscle_group'] == inc])

    selected_focus = random.sample(focus_exercises, min(3, len(focus_exercises)))
    selected_include = random.sample(include_exercises, min(2, len(include_exercises)))

    workout = []
    total_time = 0
    for ex in selected_focus + selected_include:
        weight_info = get_exercise_weight(ex['name'], ex['weight'])
        ex_copy = ex.copy()
        ex_copy['weight'] = weight_info['weight']
        ex_copy['reps'] = weight_info['reps'] or ex['reps']
        time_est = ex['sets'] * (ex['reps'] * 5 + ex['rest_seconds'])
        ex_copy['time_estimate_seconds'] = time_est
        total_time += time_est
        workout.append(ex_copy)

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
    model = config.get('xai', {}).get('model', 'grok-4-latest')
    duration = config['routine']['duration_minutes']

    # Pull workout style from config
    style = config.get('workout_style', {})
    philosophy = style.get('philosophy', 'general fitness')
    influences = ', '.join(style.get('influences', []))
    priorities = '\n'.join(f'- {p}' for p in style.get('priorities', []))
    equipment_list = _build_equipment_list(config)

    split = DAY_SPLITS[day_index]

    prompt = f"""You are an elite gym coach who programs {philosophy} workouts.
Study and draw inspiration from the training styles of: {influences}

Today is {split['name']} day. Primary focus: {split['focus']}. Also include: {', '.join(split['include'])}.

Training priorities:
{priorities}

Design a {duration}-minute workout. Use explosive compound movements, integrated multi-joint exercises,
calisthenics skills, and old school bodybuilding techniques. Think cleans, snatches, thrusters,
muscle-ups, handstand variations, supersets, and high-intensity combos.

Available equipment (ONLY use exercises that can be performed with this equipment):
{equipment_list}

For each exercise, specify which piece of equipment from the list above is used in the "equipment" field.
Output ONLY valid JSON in this exact format, no extra text or markdown:
{{"exercises": [{{"name": "Exercise Name", "sets": 3, "reps": 8, "weight": 0, "rest_seconds": 60, "equipment": "Equipment name"}}], "total_time_estimate_minutes": {duration}}}"""

    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"XAI API error: {response.status_code} {response.text}")

        result = response.json()
        content = result['choices'][0]['message']['content']
        logger.info(f"LLM response: {content}")

        # Strip markdown fences if present
        content = _strip_markdown_fences(content)
        workout_data = json.loads(content)
    except Exception as e:
        logger.error(f"XAI API failed: {e}. Falling back to static generation.")
        return generate_static_workout(day_index)

    # Apply current weights from state
    for ex in workout_data['exercises']:
        weight_info = get_exercise_weight(ex['name'], ex.get('weight', 0))
        ex['weight'] = weight_info['weight']
        ex['reps'] = weight_info['reps'] or ex['reps']

    return {
        'day': day_index,
        'exercises': workout_data['exercises'],
        'total_time_estimate_minutes': workout_data.get('total_time_estimate_minutes', duration)
    }
