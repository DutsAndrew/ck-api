from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from scripts.json_parser import json_parser
import logging

logger = logging.getLogger(__name__)


async def create_project(request: Request):
    pass