import os
#import dotenv

#dotenv.load_dotenv()
## APP
HOMEMAKER_ENDPOINT=os.getenv("HOMEMAKER_ENDPOINT")
HOMEMAKER_TOKEN = os.getenv("HOMEMAKER_TOKEN")
PRIVATE_KEY_PATH=os.getenv("PRIVATE_KEY_PATH")

##
PERCHECK_TIME_IN_SEC = int(os.getenv("PERCHECK_TIME_IN_SEC"))
LOG_FILE_SIZE = 200000000
