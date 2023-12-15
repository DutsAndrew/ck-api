from fastapi import Request
from fastapi.responses import JSONResponse

async def json_parser(request: Request):
    try:
        request_body = await request.json()
        return request_body
    except ValueError:
        # Handle invalid JSON
        return JSONResponse(content={'detail': 'invalid JSON'}, status_code=422)
    except Exception as e:
        return JSONResponse(content={'detail': f'error {e}'}, status_code=422)