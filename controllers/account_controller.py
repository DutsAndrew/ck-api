from fastapi import Request

async def delete_account(request: Request, token):
    return token