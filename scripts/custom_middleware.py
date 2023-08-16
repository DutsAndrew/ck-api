import logging

class ErrorLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            return await self.app(scope, receive, send)
        except Exception as e:
            logger = logging.getLogger("uvicorn")
            logger.error("UVICORN ERROR MIDDLEWARE: %s", str(e))
            raise e
