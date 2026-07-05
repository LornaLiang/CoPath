import json
from typing import Any

from backend.utils.errors import AppError


def parse_json(value: str, field_name: str) -> Any:
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise AppError(f"Invalid JSON stored in {field_name}", status_code=500) from exc
