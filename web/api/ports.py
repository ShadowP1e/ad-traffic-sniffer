from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from config import config
from dependencies import verify_cookie_token

router = APIRouter(prefix='/api')

@router.get("/ports", response_class=JSONResponse, dependencies=[Depends(verify_cookie_token)])
async def get_ports():
    return JSONResponse(config.SERVICES)
