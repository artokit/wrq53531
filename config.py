from dotenv import dotenv_values

config = dotenv_values('.env')
TOKEN = config['TOKEN']
HELPER_URL = config['HELPER_URL']
ADMINS = list(map(int, config['ADMINS'].split(',')))
API_ID = config['API_ID']
API_HASH = config['API_HASH']
