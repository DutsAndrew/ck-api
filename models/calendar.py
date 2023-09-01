from datetime import datetime
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

class Calendar(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    calendar_years_and_dates: dict = Field(default_factory=dict)
    calendar_holidays: list = Field(default_factory=list)
    calendar_type: str = Field(default_factory=str)
    events: list = Field(default_factory=list)
    year: int = Field(default_factory=lambda: datetime.now().year, required=True)


    def __init__(self, calendar_type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.calendar_type = calendar_type
        current_year = datetime.now().year

        if calendar_type == "personal":
            self.calendar_years_and_dates = self.generate_two_year_calendar(current_year)
            self.calendar_holidays = self.get_us_holidays()
        else:
            self.calendar_years_and_dates = self.generate_two_year_calendar(current_year)


    def generate_two_year_calendar(self, start_year):
        next_year = start_year + 1
        full_calendar = {}

        for year in [start_year, next_year]:
            year_calendar = {}
            
            for month in range(1, 13):
                _, last_day = calendar.monthrange(year, month)
                month_name = calendar.month_name[month]
                first_weekday = calendar.weekday(year, month, 1)
                
                month_info = {
                    'days': last_day,
                    'month_starts_on': calendar.day_name[first_weekday] 
                }
                
                year_calendar[month_name] = month_info
            
            full_calendar[year] = year_calendar
        
        return full_calendar
    

    def add_next_two_years_to_calendar(self, personal_calendar):
        years_list = list(personal_calendar.keys())
        last_year_in_list = years_list[-1:]
        next_year = last_year_in_list[0] + 1
        following_two_years = self.generate_two_year_calendar(next_year)
        personal_calendar.update(following_two_years)

    
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