import os
from pathlib import Path
from dotenv import load_dotenv

# Determine the project root directory
# Current file: core/config_manager.py
# Parent: core/
# Grandparent: Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

ENV_LOCAL_PATH = BASE_DIR / ".env.local"
ENV_PATH = BASE_DIR / ".env"

# Explicitly load .env.local first to override .env
if ENV_LOCAL_PATH.exists():
    load_dotenv(dotenv_path=ENV_LOCAL_PATH, override=True)

# Then load .env for any fallbacks
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

class ConfigManager:
    @staticmethod
    def get(key: str, default=None):
        return os.getenv(key, default)

    @staticmethod
    def get_required(key: str):
        """
        Retrieves an environment variable or raises an error if it's missing.
        Ensures the application fails fast if critical config is missing.
        """
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

config = ConfigManager()
