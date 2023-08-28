from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from models.bson_object_id import PyObjectId
from bson import ObjectId
import calendar
import holidays

## Calendars should have the following:
# what team or user the calendar belongs to
# what events have been created and added to calendar
# what year the calendar is for
# color scheme set by user

# CALENDARS MUST BE ACCOMPANIED BY A USER OR TEAM _ID BUT NOT BOTH

class Calendar(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    accompanied_team: Optional[PyObjectId] = Field(default_factory=None, alias="team_id")
    accompanied_user: Optional[PyObjectId] = Field(default_factory=None, alias="user_id")
    events: Optional[List[PyObjectId]] = Field(default_factory=list)
    type: str = Field(default_factory=str)
    year: int = Field(default_factory=lambda: datetime.now.year, required=True)

    def __init__(self, calendar_type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if calendar_type == "personal":
            self.calendar_days = self.get_number_of_days_in_month()
            self.holidays = self.get_us_holidays()
        else:
            self.calendar_days = self.get_number_of_days_in_month()

    def get_number_of_days_in_month(self):
        year = datetime.now().year
        full_calendar = {}

        for month in range(1, 13):
            _, last_day = calendar.monthrange(year, month)
            month_name = calendar.month_name[month]
            first_weekday = calendar.weekday(year, month, 1)

            month_info = {
                'days': last_day,
                'month_starts_on': calendar.day_name[first_weekday] 
            }

            full_calendar[month_name] = month_info

        return full_calendar
    
    def get_us_holidays(self):
        holidays_list = []
        us_holidays = holidays.US(years=datetime.now().year)

        for date, name in sorted(us_holidays.items()):
            holiday_info = {
                'date': date,
                'name': name,
                'type': 'holiday',
            }
            holidays_list.append(holiday_info)

        return holidays_list

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, PyObjectId: str},
        "json_schema_extra": {
            "example": {
                "accompanied_team": None,
                "accompanied_user": str(ObjectId()),
                "events": [str(ObjectId()), str(ObjectId())],
                "type": 'account / team',
                "year": 2023,
            }
        }
    }