from pydantic import BaseModel, Field
from typing import List
from fastapi import FastAPI
from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import calendar
import holidays
import logging
import asyncio
import certifi

class CalendarData(BaseModel):
    app_data_type: str = Field(default_factory=str)
    calendar_dates: dict = Field(default_factory=dict)
    holiday_dates: List[object] = Field(default_factory=list)

    def __init__(self, app_data_type, calendar_data, holiday_data):
        super().__init__()
        self.app_data_type = app_data_type
        self.calendar_dates = calendar_data
        self.holiday_dates = holiday_data

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
    

class UploadCalendarData:
  
    def __init__(self):
        self.app = FastAPI()
        self.start_year = datetime.now().year - 1
        self.end_year = datetime.now().year + 1

    async def upload_calendar_data(self):
        await self.setup_db_client()
        await self.store_calendar_data()
        await self.shutdown_db_client()

    async def setup_db_client(self):
        # get .env files
        config = dotenv_values("../../.env")
        self.app.mongodb_client = AsyncIOMotorClient(config["DEV_MONGO_URI"], tlsCAFile=certifi.where())
        self.app.db = self.app.mongodb_client[config["DEV_DB_NAME"]]
        return self.app

    async def shutdown_db_client(self):
        self.app.mongodb_client.close()

    def generate_calendar_data(self):
        full_calendar = {}

        for year in range(self.start_year, self.end_year + 1):
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
            
            full_calendar[str(year)] = year_calendar
        
        return full_calendar
    
    def generate_calendar_holidays(self):
        full_holiday_calendar = {}

        for year in range(self.start_year, self.end_year + 1):
            holiday_calendar = []

            us_holidays = holidays.US(years=year)

            for date, name in sorted(us_holidays.items()):
                holiday_info = {
                    'date': date.strftime("%Y-%m-%d"),  # Convert to string,
                    'name': name,
                    'type': 'holiday',
                }
                holiday_calendar.append(holiday_info)

            full_holiday_calendar[str(year)] = holiday_calendar

        return full_holiday_calendar

    async def store_calendar_data(self):
        
        # Configure the logging settings
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        calendar_data = CalendarData(
            'calendar',
            self.generate_calendar_data(),
            self.generate_calendar_holidays()
        )
        
        try:
            converted_data = calendar_data.model_dump() # convert data to dict for storing
            check_for_old_data = await self.app.db['app-data'].find_one(
                {"app_data_type": 'calendar'}
            )

            print(check_for_old_data)

            if check_for_old_data is not None:
                data_upload = await self.app.db['app-data'].update_one(
                    {"app_data_type": 'calendar'},
                    {"$set": converted_data},
                )
            else:
                data_upload = await self.app.db['app-data'].insert_one(converted_data)

            if data_upload is not None:
                logger.info("Data uploaded successfully")
                await self.shutdown_db_client()
                return {
                    "detail": "Data uploaded",
                    "data": data_upload,
                }
            else:
                logger.error("There was an error processing the upload")
                await self.shutdown_db_client()
                return {
                    "detail": "There may have been an error with the insertion request",
                }
            
        except Exception as e:
            logger.exception("There was a server error uploading data")
            await self.shutdown_db_client()
            return {
                "detail": "There was an error uploading the data to MongoDB",
                "errors": str(e),
            }, 500
        

if __name__ == "__main__":
    uploader = UploadCalendarData()
    asyncio.run(uploader.upload_calendar_data())