import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REFRESH_INTERVAL_MINUTES = 30
CACHE_TTL_SECONDS = 1800
