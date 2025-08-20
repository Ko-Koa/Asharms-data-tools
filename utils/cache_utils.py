import os
import json
from typing import Any

from settings.projectEnv import ProjectEnv


def write_cache(cache_name: str, data: Any):
    file_path = os.path.join(ProjectEnv.cachePath, f"{cache_name}.json")
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_cache(cache_name: str) -> Any:
    file_path = os.path.join(ProjectEnv.cachePath, f"{cache_name}.json")
    if not os.path.exists(file_path):
        return {}

    with open(
        os.path.join(ProjectEnv.cachePath, f"{cache_name}.json"), "r", encoding="utf-8"
    ) as f:
        return json.loads(f.read())
