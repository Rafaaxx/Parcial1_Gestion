"""Input sanitization utilities for XSS prevention"""

import html
from functools import wraps
from typing import Any, Dict, List, Union


def escape_html(text: str) -> str:
    """
    Escape HTML entities to prevent XSS attacks.

    Converts characters like <, >, &, ", ' to their HTML entity equivalents.

    Args:
        text: The string to sanitize

    Returns:
        Sanitized string with HTML entities escaped
    """
    return html.escape(text, quote=True)


def sanitize_string(value: Union[str, None]) -> Union[str, None]:
    """
    Sanitize a string value, escaping HTML entities.

    Args:
        value: The string to sanitize (can be None)

    Returns:
        Sanitized string or None if input was None
    """
    if value is None:
        return None
    return escape_html(str(value))


def sanitize_dict(data: Dict[str, Any], keys_to_sanitize: List[str] = None) -> Dict[str, Any]:
    """
    Recursively sanitize string values in a dictionary.

    Args:
        data: The dictionary to sanitize
        keys_to_sanitize: Optional list of specific keys to sanitize.
                         If None, sanitizes all string values.

    Returns:
        Dictionary with sanitized string values
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Sanitize if key is in the list or no list specified (sanitize all)
            if keys_to_sanitize is None or key in keys_to_sanitize:
                result[key] = escape_html(value)
            else:
                result[key] = value
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value, keys_to_sanitize)
        elif isinstance(value, list):
            result[key] = [
                (
                    sanitize_dict(item, keys_to_sanitize)
                    if isinstance(item, dict)
                    else (
                        escape_html(item)
                        if isinstance(item, str)
                        and (keys_to_sanitize is None or key in keys_to_sanitize)
                        else item
                    )
                )
                for item in value
            ]
        else:
            result[key] = value

    return result


def sanitize_for_sql(value: Any) -> Any:
    """
    Sanitize value for SQL (placeholder - ORM already handles this).

    Note: Using SQLModel/SQLAlchemy with parameterized queries already
    protects against SQL injection. This function is a no-op but
    exists for interface consistency.

    Args:
        value: The value to sanitize

    Returns:
        The value unchanged (ORM handles sanitization)
    """
    return value


# Fields that commonly contain user input and should be sanitized
DEFAULT_SANITIZE_FIELDS = [
    "name",
    "description",
    "address",
    "calle",
    "ciudad",
    "barrio",
    "observaciones",
    "titulo",
    "contenido",
    "email",  # Also escape to be safe
]


def sanitize_pydantic_model_fields(model_instance, fields: List[str] = None) -> None:
    """
    Sanitize specified fields of a Pydantic model in-place.

    Args:
        model_instance: An instance of a Pydantic model
        fields: List of field names to sanitize. Defaults to DEFAULT_SANITIZE_FIELDS

    Example:
        class UserCreate(BaseModel):
            name: str
            email: str

        user = UserCreate(name="<script>alert('xss')</script>", email="test@example.com")
        sanitize_pydantic_model_fields(user)
        print(user.name)  # &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;
    """
    fields_to_sanitize = fields or DEFAULT_SANITIZE_FIELDS

    for field_name in fields_to_sanitize:
        if hasattr(model_instance, field_name):
            value = getattr(model_instance, field_name)
            if isinstance(value, str):
                setattr(model_instance, field_name, escape_html(value))
