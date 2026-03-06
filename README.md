# Gym Routine Email Agent

This agent sends you a 40-minute calisthenics-style gym routine via email 5 days a week, including exercises, sets, reps, weights, and rest times. It also checks for replies to adjust weights or reps.

## Setup

1. Clone or download this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Get an XAI API key: Sign up at https://x.ai/api and generate a key.
4. Copy `config.yml.example` to `config.yml` and fill in:
   - Your Gmail credentials (enable 2FA and generate an app password).
   - Your XAI API key.
5. Run the agent: `python main.py`

## Configuration

Edit `config.yml`:
- Email settings: SMTP/IMAP servers, credentials.
- Schedule: Days and time to send emails.
- Routine: Exercises with default weights, etc.

## How it works

- Generates a workout based on the day (push, pull, legs, etc.).
- Sends an email with the routine.
- Checks for replies and parses adjustments to update state.

## Testing

Run tests: `python -m pytest tests/`