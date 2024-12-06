import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers.auth import router as auth_router
from routers.pages import router as pages_router
from api.chain import router as api_chain_router
from api.log import router as api_log_router
from api.generate_code import router as api_code_router
from api.traffic_dump import router as api_traffic_router
from api.ports import router as api_ports_router
from config import config

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)

app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(api_chain_router)
app.include_router(api_log_router)
app.include_router(api_code_router)
app.include_router(api_traffic_router)
app.include_router(api_ports_router)

if __name__ == '__main__':
    import uvicorn
    os.makedirs(os.path.join('..', 'database'), exist_ok=True)
    os.makedirs(os.path.join('..', 'dump'), exist_ok=True)

    uvicorn.run(app, host=config.APP_HOST, port=int(config.APP_PORT))
