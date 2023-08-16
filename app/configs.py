import datetime

BASE_URL = 'http://localhost:5000'
DB_PATH = './app/database/'
IMAGES_PATH = './app/static/images/'
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=6)