"""Time helpers shared by legacy naive-UTC database fields."""
from datetime import datetime, timezone

def utcnow() -> datetime:
    """Return current UTC as naive datetime for existing DB DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
