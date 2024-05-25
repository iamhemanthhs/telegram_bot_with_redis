import redis


REDIS_LOCK_NAME = "my_lock"
redis_client = redis.Redis(host='redis-16105.c11.us-east-1-3.ec2.redns.redis-cloud.com', port=16105, db=0, password='<REDIS_PASSWORD>')

BOT_TOKEN = "<BOT_TOKEN>"


IMAGE_PATH = "x.jpg"
PASSWORD = "<REQUIRED_PASSWORD>"

REPLAY_MESSAGE = "please enter your password..."

MAIN_ACCOUNT_USER_ID = "6516231750"