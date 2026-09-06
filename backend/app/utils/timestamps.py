"""
Timestamp formatting utilities.
Convert seconds to [M:SS] format and related utilities.
"""

from typing import Optional


def seconds_to_timestamp(seconds: float, precision: str = 'integer') -> str:
    """
    Convert seconds to timestamp format.

    Args:
        seconds: Duration in seconds.
        precision: 'integer' for [M:SS], 'decimal' for [M:SS.SS].

    Returns:
        Formatted timestamp string.

    Examples:
        >>> seconds_to_timestamp(7.84)
        '[0:07]'
        >>> seconds_to_timestamp(7.84, 'decimal')
        '[0:07.84]'
        >>> seconds_to_timestamp(127.5)
        '[2:07]'
    """
    total_seconds = int(seconds) if precision == 'integer' else seconds

    if precision == 'integer':
        minutes = int(total_seconds) // 60
        secs = int(total_seconds) % 60
        return f'[{minutes}:{secs:02d}]'
    else:
        minutes = int(total_seconds) // 60
        secs = total_seconds % 60
        return f'[{minutes}:{secs:05.2f}]'


def timestamp_to_seconds(timestamp: str) -> float:
    """
    Convert timestamp format back to seconds.

    Args:
        timestamp: Timestamp in format [M:SS] or [M:SS.SS].

    Returns:
        Duration in seconds.

    Examples:
        >>> timestamp_to_seconds('[0:07]')
        7.0
        >>> timestamp_to_seconds('[2:30.50]')
        150.5
    """
    # Remove brackets
    ts = timestamp.strip('[]')

    # Split on colon
    parts = ts.split(':')
    if len(parts) != 2:
        raise ValueError(f"Invalid timestamp format: {timestamp}")

    minutes = int(parts[0])
    seconds = float(parts[1])

    return minutes * 60 + seconds


def format_duration(seconds: float) -> str:
    """
    Format duration for display.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted string like "4m 56s" or "2h 5m 30s".

    Examples:
        >>> format_duration(296)
        '4m 56s'
        >>> format_duration(7425)
        '2h 5m 25s'
    """
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    secs = int(seconds) % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"
