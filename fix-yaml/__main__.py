import json
import logging
import subprocess
import sys
from typing import List

import yaml
from github import Github, GithubException
from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    input_token: SecretStr
    input_target_repository: str
    input_file_path: str
    input_target_branch: str
    input_commit_message: str
    input_key_val_pairs: List[str]


logging.basicConfig(level=logging.INFO)
settings = Settings()

logging.info("Setting up GitHub Actions git user")
subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
subprocess.run(
    ["git", "config", "user.email", "github-actions@github.com"],
    check=True,
)

logging.info(f"Using config: {settings.json()}")
logging.info(
    "Finding target file in target repository: "
    f"{settings.input_target_branch}/{settings.input_file_path}"
)
g = Github(settings.input_token.get_secret_value())
try:
    target_repo = g.get_repo(settings.input_target_repository)
except GithubException.UnknownObjectException:
    logging.error(f"Repository {settings.input_target_repository} not found")
    sys.exit(1)

try:
    target_file = target_repo.get_contents(
        settings.input_file_path, ref=settings.input_target_branch
    )
except GithubException.UnknownObjectException:
    logging.error(
        f"In branch {settings.input_target_branch}, "
        "file {settings.input_file_path} not found"
    )
    sys.exit(1)

logging.info("Parsing key-val pairs")
kv_json = json.loads(settings.input_key_val_pairs)
kv_list = []
for key, val in kv_json.items():
    keys = key.split(".")
    kv_list.append([keys, val.strip()])


logging.info("Updating target yaml file")
try:
    values = yaml.safe_load(target_file.decoded_content)
except yaml.YAMLError as exc:
    logging.error(f"The File is an invalid yaml\n {exc}")
    sys.exit(1)


def update_dict(keys: List[str], val: str, values: dict):
    if len(keys) == 1:
        values[keys[0]] = val
        return values
    else:
        if keys[0] not in values:
            raise KeyError(f"Key {keys[0]} not found in yaml")
        return update_dict(keys[1:], val, values[keys[0]])


for each in kv_list:
    key = each[0]
    val = each[1]
    logging.info(f"Updating {key} with {val}")
    try:
        values = update_dict(key, values)
    except KeyError:
        sys.exit(1)

new_values = yaml.dump(values, default_flow_style=False, sort_keys=False)

logging.info("Committing changes to target repository")
target_repo.update_file(
    settings.input_file_path,
    settings.input_commit_message,
    new_values,
    target_file.sha,
)
