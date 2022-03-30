import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from github import Github
from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    github_repository: str
    github_event_path: Path
    github_event_name: Optional[str] = None
    input_token: SecretStr


logging.basicConfig(level=logging.INFO)
settings = Settings()
logging.info(f"Using config: {settings.json()}")
g = Github(settings.input_token.get_secret_value())
repo = g.get_repo(settings.github_repository)
