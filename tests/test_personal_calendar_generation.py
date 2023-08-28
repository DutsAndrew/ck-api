import pytest
from models.calendar import Calendar
from datetime import datetime

# @pytest.mark.skip(reason='Not implemented')
def test_personal_calendar_gets_created():
    new_calendar = Calendar(calendar_type="personal")

    assert len(new_calendar.calendar_days) == 12
    assert isinstance(new_calendar.calendar_days['January']['days'], int)
    assert isinstance(new_calendar.calendar_days['February']['month_starts_on'], str)

    assert len(new_calendar.calendar_holidays) != 0
    assert 'date' in new_calendar.calendar_holidays[0]
    assert new_calendar.calendar_holidays[0]['name'] == "New Year's Day"
    assert new_calendar.calendar_holidays[0]['type'] == "holiday"