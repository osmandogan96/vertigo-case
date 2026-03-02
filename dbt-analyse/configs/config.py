import os
from dotenv import load_dotenv

CWD = os.path.dirname(os.path.realpath(__file__))
MAIN_PATH = os.path.realpath(os.path.join(CWD, '..'))

env_path = os.path.join(CWD, '.env')
load_dotenv(env_path)

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
