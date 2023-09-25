import pytest
from models.calendar import Calendar
from datetime import datetime

# @pytest.mark.skip(reason='Not implemented')
def test_personal_calendar_gets_created():
    new_calendar = Calendar(calendar_type="personal", name="Bob", UserId='123')

    current_year = datetime.now().year
    next_year = current_year + 1

    assert len(new_calendar.calendar_years_and_dates[current_year]) == 12
    assert len(new_calendar.calendar_years_and_dates[next_year]) == 12
    assert isinstance(new_calendar.calendar_years_and_dates[current_year]['January']['days'], int)
    assert isinstance(new_calendar.calendar_years_and_dates[next_year]['January']['days'], int)

    assert isinstance(new_calendar.calendar_years_and_dates[current_year]['February']['month_starts_on'], str)
    assert isinstance(new_calendar.calendar_years_and_dates[next_year]['February']['month_starts_on'], str)

    assert len(new_calendar.calendar_holidays) != 0
    assert len(new_calendar.calendar_holidays) != 0

    assert 'date' in new_calendar.calendar_holidays[0]
    assert new_calendar.calendar_holidays[0]['name'] == "New Year's Day"
    assert new_calendar.calendar_holidays[0]['type'] == "holiday"