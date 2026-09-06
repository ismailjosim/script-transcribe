"""
Tests for timestamp utilities.
"""

from app.utils.timestamps import seconds_to_timestamp, timestamp_to_seconds, format_duration


def test_seconds_to_timestamp_integer():
    """Test conversion to [M:SS] format."""
    assert seconds_to_timestamp(7.84) == '[0:07]'
    assert seconds_to_timestamp(127.5) == '[2:07]'
    assert seconds_to_timestamp(0) == '[0:00]'
    assert seconds_to_timestamp(59) == '[0:59]'
    assert seconds_to_timestamp(60) == '[1:00]'


def test_seconds_to_timestamp_decimal():
    """Test conversion to [M:SS.SS] format."""
    assert seconds_to_timestamp(7.84, 'decimal') == '[0:07.84]'
    assert seconds_to_timestamp(127.5, 'decimal') == '[2:07.50]'


def test_timestamp_to_seconds():
    """Test conversion back to seconds."""
    assert timestamp_to_seconds('[0:07]') == 7.0
    assert timestamp_to_seconds('[2:30]') == 150.0
    assert timestamp_to_seconds('[2:30.50]') == 150.5


def test_format_duration():
    """Test duration formatting."""
    assert format_duration(296) == '4m 56s'
    assert format_duration(7425) == '2h 3m 45s'
    assert format_duration(45) == '45s'
