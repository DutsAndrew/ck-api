from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AppData():

    @staticmethod
    async def get_calendar_app_data(request: Request):
          try:
              calendar_data_lookup = await request.app.db['app-data'].find_one(
                  {"app_data_type": "calendar"}
              )

              if calendar_data_lookup is None:
                  raise HTTPException(
                      status_code=404,
                      detail='Calendar data not found',
                  )
                  
              converted_data = dict(calendar_data_lookup)
              if "_id" in converted_data:
                  converted_data["_id"] = str(converted_data["_id"])

              return JSONResponse(
                  content={
                      'detail': 'Calendar Data Loaded',
                      'data': converted_data,
                  },
                  status_code=200
              )
                
          except Exception as e:
              logger.error(f"Error processing request: {e}")
              return JSONResponse(
                  content={
                      'detail': 'There was an issue processing your request',
                  },
                  status_code=500
              )