import imaplib
import email
import requests
from .config import load_config
from .state import update_last_email_uid, get_last_email_uid
from .parser import parse_adjustments
from .state import update_exercise_weight
import logging

logger = logging.getLogger(__name__)


def send_workout_email(workout):
    config = load_config()
    email_config = config['email']
    api_key = config['resend_api_key']

    body = "Good Morning Jonathan - GET READY FOR YOUR WORKOUT ! don't slack get this routine in!!!\n\n"
    body += f"Today's workout (approx {workout['total_time_estimate_minutes']} min):\n\n"
    for ex in workout['exercises']:
        equipment_str = f" | Equipment: {ex['equipment']}" if ex.get('equipment') else ""
        body += f"- {ex['name']}: {ex['sets']} sets x {ex['reps']} reps @ {ex['weight']} lbs, rest {ex['rest_seconds']}s{equipment_str}\n\n"
    body += "\nReply to this email with adjustments, e.g. 'Increase bench to 90 lbs' or 'Did 10 reps on pull-ups'."

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": email_config['sender'],
                "to": [email_config['recipient']],
                "subject": f"Gym Routine for Day {workout['day'] + 1}",
                "text": body
            }
        )
        if response.status_code in (200, 201):
            result = response.json()
            logger.info(f"Workout email sent. Resend ID: {result.get('id', 'unknown')}")
        else:
            logger.error(f"Resend API error: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


def check_for_replies():
    config = load_config()['email']
    try:
        mail = imaplib.IMAP4_SSL(config['imap_server'])
        mail.login(config['username'], config['password'])
        mail.select('inbox')

        last_uid = get_last_email_uid()
        if last_uid:
            status, messages = mail.search(None, f'UID {int(last_uid)+1}:*')
        else:
            status, messages = mail.search(None, 'ALL')

        if status == 'OK':
            for num in messages[0].split():
                status, data = mail.fetch(num, '(RFC822)')
                if status == 'OK':
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    if msg['From'] == config['recipient']:
                        body = get_email_body(msg)
                        adjustments = parse_adjustments(body)
                        for adj in adjustments:
                            update_exercise_weight(adj['exercise'], adj['weight'], adj['reps'])
                        update_last_email_uid(num.decode())
        mail.logout()
    except Exception as e:
        logger.error(f"Failed to check emails: {e}")


def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return ""
