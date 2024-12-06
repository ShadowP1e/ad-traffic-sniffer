import os

from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import FileResponse

from api import verify_cookie_token
from config import config


router = APIRouter(prefix='')


@router.get("/download-traffic-dump", response_class=FileResponse, dependencies=[Depends(verify_cookie_token)])
async def download_traffic_dump():
    if not os.path.exists(config.TRAFFIC_DUMP_FILE_PATH):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(config.TRAFFIC_DUMP_FILE_PATH, filename="traffic_dump.pcap")
