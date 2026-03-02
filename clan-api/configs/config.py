import os
import urllib.parse
from dotenv import load_dotenv

CWD = os.path.dirname(os.path.realpath(__file__))
MAIN_PATH = os.path.realpath(os.path.join(CWD, '..'))

# Load .env file if it exists (local dev only, Cloud Run uses env vars directly)
env_path = os.path.join(CWD, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

PROJECT_NAME = "Clan API"
PROJECT_VERSION = "1.0.0"

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = urllib.parse.quote_plus(os.getenv("POSTGRES_PASSWORD", "postgres"))
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "vertigo_clans")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)