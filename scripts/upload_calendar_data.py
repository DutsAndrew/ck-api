from fastapi import FastAPI
from dotenv import dotenv_values
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import json_util
import calendar
import holidays
import logging
import asyncio
import certifi

class UploadCalendarData:
  
    def __init__(self):
        self.app = FastAPI()
        self.start_year = datetime.now().year - 5
        self.end_year = datetime.now().year + 5

    async def upload_calendar_data(self):
        await self.setup_db_client()
        await self.store_calendar_data()
        await self.shutdown_db_client()

    async def setup_db_client(self):
        # get .env files
        config = dotenv_values("../.env")
        self.app.mongodb_client = AsyncIOMotorClient(config["DEV_MONGO_URI"], tlsCAFile=certifi.where())
        self.app.db = self.app.mongodb_client[config["DEV_DB_NAME"]]
        return self.app

    async def shutdown_db_client(self):
        self.app.mongodb_client.close()

    def generate_calendar_data(self):
        full_calendar = {}

        for year in [self.start_year, self.end_year]:
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
        
        return json_util.dumps(full_calendar) # convert to JSON string
    
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

        return json_util.dumps(full_holiday_calendar) # convert to JSON string

    async def store_calendar_data(self):
        
        # Configure the logging settings
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        calendar_data = {
            "dates_info": self.generate_calendar_data(),
            "holidays_info": self.generate_calendar_holidays(),
        }
        
        try:
            data_upload = await self.app.db['calendar-data'].insert_one(calendar_data)

            if data_upload is not None:
                logger.info("Data uploaded successfully")
                return {
                    "detail": "Data uploaded",
                    "data": data_upload,
                }
            else:
                logger.error("There was an error processing the upload")
                return {
                    "detail": "There may have been an error with the insertion request",
                }
            
        except Exception as e:
            logger.exception("There was a server error uploading data")
            return {
                "detail": "There was an error uploading the data to MongoDB",
                "errors": str(e),
            }, 500
        

if __name__ == "__main__":
    uploader = UploadCalendarData()
    asyncio.run(uploader.upload_calendar_data())