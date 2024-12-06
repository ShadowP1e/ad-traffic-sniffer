from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from config import config
from routers import templates

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/authenticate")
async def authenticate(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == config.VALID_USERNAME and password == config.VALID_PASSWORD:
        response = RedirectResponse(url="/logs", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key=config.API_KEY_COOKIE_NAME, value=config.API_KEY_COOKIE_VALUE)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неправильные имя пользователя или пароль"})

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(config.API_KEY_COOKIE_NAME)
    return response
