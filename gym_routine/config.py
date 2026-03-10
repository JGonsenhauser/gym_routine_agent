import yaml
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def load_config(config_path=None):
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    # Override with env vars
    if 'xai' not in config or config['xai'] is None:
        config['xai'] = {}
    config['xai']['api_key'] = os.getenv('XAI_API_KEY', config['xai'].get('api_key', ''))
    config['resend_api_key'] = os.getenv('RESEND_API_KEY', '')
    return config