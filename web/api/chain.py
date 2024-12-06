from datetime import datetime

from fastapi import Depends, HTTPException, APIRouter
from starlette.responses import JSONResponse

from api import storage, verify_cookie_token


router = APIRouter(prefix='/api')


@router.get("/chains", response_class=JSONResponse, dependencies=[Depends(verify_cookie_token)])
async def chains_page(
    limit: int = 1000,
    offset: int = 0,
    source_ip: str | None = None,
    port: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
):
    chains = storage.fetch_chains(
        source_ip=source_ip,
        port=port,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    return JSONResponse(chains)


@router.get("/check-updates-chains", dependencies=[Depends(verify_cookie_token)])
async def check_updates_chains(
    last_timestamp: int | None = None,
    source_ip: str | None = None,
    port: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None
):
    new_chains = storage.get_updated_chains(
        last_timestamp=last_timestamp,
        source_ip=source_ip,
        port=port,
        start_time=start_time,
        end_time=end_time
    ) if last_timestamp else storage.fetch_chains(
        source_ip=source_ip,
        port=port,
        start_time=start_time,
        end_time=end_time,
        limit=10
    )
    return {"new_chains": new_chains}


@router.get("/chains/{chain_id}")
async def get_chain(chain_id: int):
    chain = storage.get_chain_by_id(chain_id)
    if chain is None:
        raise HTTPException(status_code=404, detail="Chain not found")
    return chain
