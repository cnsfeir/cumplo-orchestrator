import os

from dotenv import load_dotenv

load_dotenv()

# Basics
PROJECT_ID = os.getenv("PROJECT_ID", "cumplo-orchestrator")
LOCATION = os.getenv("LOCATION", "us-central1")
IS_TESTING = bool(os.getenv("IS_TESTING"))
LOG_FORMAT = "\n%(levelname)s: %(message)s"
