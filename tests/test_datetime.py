from datetime import datetime

from mestolo.datetime import DateTimeInterval


def test_datetime_interval_hashes():
    start = datetime(2022, 1, 1, 1, 1, 1)
    end =  datetime(2024, 1, 1, 1, 1, 1)
    interval = DateTimeInterval(start, end)
    h = hash(interval)
    assert h is not None

def test_datetime_interval_includes_with_bounds():
    start = datetime(2022, 1, 1, 1, 1, 1)
    end =  datetime(2024, 1, 1, 1, 1, 1)
    interval = DateTimeInterval(start, end)
    assert interval.includes(datetime(2023, 1, 1, 1, 1, 1))

def test_datetime_interval_includes_with_open_start():
    start = None
    end =  datetime(2024, 1, 1, 1, 1, 1)
    interval = DateTimeInterval(start, end)
    assert interval.includes(datetime(2023, 1, 1, 1, 1, 1))

def test_datetime_interval_includes_with_open_end():
    start = datetime(2022, 1, 1, 1, 1, 1)
    end =  None
    interval = DateTimeInterval(start, end)
    assert interval.includes(datetime(2023, 1, 1, 1, 1, 1))

def test_datetime_interval_includes_both_open():
    start = None
    end = None
    interval = DateTimeInterval(start, end)
    assert interval.includes(datetime(2023, 1, 1, 1, 1, 1))
