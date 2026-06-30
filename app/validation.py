"""
Lightweight request validation for the Task resource.
No external validation library required, keeps the project dependency-light.
"""

ALLOWED_STATUSES = {"TODO", "IN_PROGRESS", "DONE"}


def validate_task_payload(data: dict, partial: bool = False) -> tuple[bool, str | None]:
    """
    Validates incoming JSON for creating/updating a task.
    Returns (is_valid, error_message).
    """
    if not isinstance(data, dict):
        return False, "Request body must be a JSON object."

    if not partial and "title" not in data:
        return False, "'title' is required."

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return False, "'title' must be a non-empty string."

    if "status" in data:
        if data["status"] not in ALLOWED_STATUSES:
            return False, f"'status' must be one of {sorted(ALLOWED_STATUSES)}."

    if "priority" in data:
        if not isinstance(data["priority"], int) or not (1 <= data["priority"] <= 5):
            return False, "'priority' must be an integer between 1 and 5."

    return True, None
