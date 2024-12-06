from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

from api import storage, verify_cookie_token

router = APIRouter(prefix='/api')


@router.get("/logs", response_class=JSONResponse, dependencies=[Depends(verify_cookie_token)])
async def logs_page(
    source_ip: str | None = None,
    port: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = 1000,
    offset: int = 0
):
    logs = storage.fetch_logs(
        source_ip=source_ip,
        port=port,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    return JSONResponse(logs)


@router.get("/check-updates-logs", dependencies=[Depends(verify_cookie_token)])
async def check_updates_logs(
    last_log_id: int | None = None,
    source_ip: str | None = None,
    port: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None
):
    if last_log_id:
        new_logs = storage.get_new_logs(last_log_id, source_ip, port, start_time, end_time)
    else:
        new_logs = storage.fetch_logs(limit=10, source_ip=source_ip, port=port, start_time=start_time, end_time=end_time)
    return {"new_logs": new_logs}


@router.get("/logs/{log_id}", dependencies=[Depends(verify_cookie_token)])
async def get_log(log_id: int):
    log = storage.get_log_by_id(log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
