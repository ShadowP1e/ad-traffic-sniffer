import asyncio
import os
import shutil
import tempfile

from api import verify_cookie_token
from config import config
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix='')

async def delete_file_after_delay(file_path: str, delay_seconds: int):
    await asyncio.sleep(delay_seconds)
    if os.path.exists(file_path):
        os.remove(file_path)

@router.get("/download-traffic-dump", response_class=FileResponse, dependencies=[Depends(verify_cookie_token)])
async def download_traffic_dump(background_tasks: BackgroundTasks):
    if not os.path.exists(config.TRAFFIC_DUMP_FILE_PATH):
        raise HTTPException(status_code=404, detail="File not found")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_name = temp_file.name
        shutil.copy(config.TRAFFIC_DUMP_FILE_PATH, temp_file_name)

    background_tasks.add_task(delete_file_after_delay, temp_file_name, 600)

    response = FileResponse(temp_file_name, filename="traffic_dump.pcap")
    return response
