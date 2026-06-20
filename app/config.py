import os
from dotenv import load_dotenv

load_dotenv()

FANAR_API_KEY = os.getenv("FANAR_API_KEY", "")
FANAR_API_BASE = os.getenv("FANAR_API_BASE", "https://api.fanar.qa/v1")
FANAR_MODEL = os.getenv("FANAR_MODEL", "Fanar-C-2-27B")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "10"))
PROFILES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "profiles")
INDICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "indices")
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
MOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mock")
