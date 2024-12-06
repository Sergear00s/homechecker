import os
from dotenv import load_dotenv

load_dotenv()
INTRA_APP_PUBLIC = os.getenv("INTRA_APP_PUBLIC")
INTRA_APP_SECRET = os.getenv("INTRA_APP_SECRET")
HOMEMAKER_ENDPOINT=os.getenv("HOMEMAKER_ENDPOINT")
HOMEMAKER_TOKEN = os.getenv("HOMEMAKER_TOKEN")

PERCHECK_TIME_IN_SEC = 600 