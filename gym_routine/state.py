import json
import os
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(__file__), '..', 'state.json')

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        'week_index': 0,
        'exercise_weights': {},
        'last_email_uid': None,
        'last_check_time': None
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def update_exercise_weight(exercise_name, new_weight, new_reps=None):
    state = load_state()
    if exercise_name not in state['exercise_weights']:
        state['exercise_weights'][exercise_name] = {'weight': new_weight, 'reps': new_reps or 0}
    else:
        state['exercise_weights'][exercise_name]['weight'] = new_weight
        if new_reps is not None:
            state['exercise_weights'][exercise_name]['reps'] = new_reps
    save_state(state)

def get_exercise_weight(exercise_name, default_weight=0):
    state = load_state()
    return state['exercise_weights'].get(exercise_name, {'weight': default_weight, 'reps': 0})

def increment_week():
    state = load_state()
    state['week_index'] = (state['week_index'] + 1) % 5  # Assuming 5-day rotation
    save_state(state)

def get_week_index():
    return load_state()['week_index']

def update_last_email_uid(uid):
    state = load_state()
    state['last_email_uid'] = uid
    state['last_check_time'] = datetime.now().isoformat()
    save_state(state)

def get_last_email_uid():
    return load_state()['last_email_uid']