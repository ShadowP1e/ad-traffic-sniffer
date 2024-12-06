from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from config import config
from modules.storage import Storage
from dependencies import verify_cookie_token
from routers import templates

router = APIRouter()
storage = Storage(config.DATABASE_PATH)

@router.get("/logs", response_class=HTMLResponse, dependencies=[Depends(verify_cookie_token)])
async def logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

@router.get("/chains", response_class=HTMLResponse, dependencies=[Depends(verify_cookie_token)])
async def chains_page(request: Request):
    return templates.TemplateResponse("chains.html", {"request": request})
