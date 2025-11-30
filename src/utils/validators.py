"""Validation utility functions."""
import re
from typing import Any, List, Dict, Optional
from datetime import datetime
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email address.
    Returns (is_valid, error_message)
    """
    try:
        # Use email-validator library for robust validation
        validate_email_lib(email)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)
    except:
        # Fallback to regex if library not available
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, None
        return False, "Invalid email format"


def validate_phone(phone: str, country_code: str = "US") -> tuple[bool, Optional[str]]:
    """Validate phone number."""
    # Remove common formatting characters
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Basic validation (10-15 digits)
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False, "Phone number must be between 10-15 digits"
    
    # Check if it starts with + for international
    if cleaned.startswith('+'):
        if len(cleaned) < 11:
            return False, "International number too short"
    
    return True, None


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """Validate URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if url_pattern.match(url):
        return True, None
    return False, "Invalid URL format"


def validate_date(date_string: str) -> tuple[bool, Optional[str]]:
    """Validate date string."""
    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%d-%m-%Y"
    ]
    
    for fmt in date_formats:
        try:
            datetime.strptime(date_string, fmt)
            return True, None
        except ValueError:
            continue
    
    return False, "Invalid date format. Use YYYY-MM-DD"


def validate_password(password: str, min_length: int = 8) -> tuple[bool, List[str]]:
    """
    Validate password strength.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple[bool, List[str]]:
    """Validate that required fields are present."""
    missing = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing.append(field)
    
    if missing:
        return False, missing
    return True, []


def validate_string_length(text: str, min_length: int = 0, 
                          max_length: int = None) -> tuple[bool, Optional[str]]:
    """Validate string length."""
    length = len(text)
    
    if length < min_length:
        return False, f"Text must be at least {min_length} characters"
    
    if max_length and length > max_length:
        return False, f"Text must not exceed {max_length} characters"
    
    return True, None


def validate_number_range(number: float, min_value: float = None, 
                         max_value: float = None) -> tuple[bool, Optional[str]]:
    """Validate number is within range."""
    if min_value is not None and number < min_value:
        return False, f"Number must be at least {min_value}"
    
    if max_value is not None and number > max_value:
        return False, f"Number must not exceed {max_value}"
    
    return True, None


def validate_enum(value: str, allowed_values: List[str]) -> tuple[bool, Optional[str]]:
    """Validate value is in allowed list."""
    if value in allowed_values:
        return True, None
    
    return False, f"Value must be one of: {', '.join(allowed_values)}"


def validate_uuid(uuid_string: str) -> tuple[bool, Optional[str]]:
    """Validate UUID format."""
    uuid_pattern = re.compile(
        r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        re.IGNORECASE
    )
    
    if uuid_pattern.match(uuid_string):
        return True, None
    return False, "Invalid UUID format"


def validate_json(json_string: str) -> tuple[bool, Optional[str]]:
    """Validate JSON string."""
    import json
    
    try:
        json.loads(json_string)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"


def validate_time_range(start_time: datetime, end_time: datetime) -> tuple[bool, Optional[str]]:
    """Validate time range."""
    if start_time >= end_time:
        return False, "Start time must be before end time"
    
    return True, None


def validate_file_type(filename: str, allowed_extensions: List[str]) -> tuple[bool, Optional[str]]:
    """Validate file extension."""
    extension = filename.split('.')[-1].lower()
    
    if extension in [ext.lower().lstrip('.') for ext in allowed_extensions]:
        return True, None
    
    return False, f"File type must be one of: {', '.join(allowed_extensions)}"


def validate_priority(priority: str) -> tuple[bool, Optional[str]]:
    """Validate task priority."""
    valid_priorities = ["low", "medium", "high", "urgent"]
    return validate_enum(priority.lower(), valid_priorities)


def validate_timezone(timezone: str) -> tuple[bool, Optional[str]]:
    """Validate timezone string."""
    try:
        import pytz
        if timezone in pytz.all_timezones:
            return True, None
        return False, "Invalid timezone"
    except:
        # Basic validation if pytz not available
        if re.match(r'^[A-Za-z_/]+$', timezone):
            return True, None
        return False, "Invalid timezone format"


def sanitize_input(text: str, allow_html: bool = False) -> str:
    """Sanitize user input to prevent XSS."""
    if not allow_html:
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
    
    # Remove dangerous characters
    text = text.replace('<script>', '').replace('</script>', '')
    text = text.replace('javascript:', '')
    text = text.replace('onerror=', '')
    text = text.replace('onload=', '')
    
    return text.strip()


class ValidationError(Exception):
    """Custom validation error."""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"message": self.message}
        if self.field:
            result["field"] = self.field
        return result