import tempfile

from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import FileResponse

from utils.code_writer import generate_code_for_log, generate_code_for_chain
from api import storage, verify_cookie_token


router = APIRouter(prefix='/api')


@router.get("/generate_code/log/{log_id}", dependencies=[Depends(verify_cookie_token)])
async def get_python_code_for_log(log_id: int):
    log_data = storage.get_log_by_id(log_id)
    if not log_data:
        raise HTTPException(status_code=404, detail="Log not found")

    python_code = generate_code_for_log(log_data)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
        tmp_file.write(python_code.encode())
        tmp_file_path = tmp_file.name

    return FileResponse(tmp_file_path, filename="request_code.py", media_type="application/octet-stream")


@router.get("/generate_code/chain/{chain_id}", dependencies=[Depends(verify_cookie_token)])
async def get_python_code_for_chain(chain_id: int):
    chain_data = storage.get_chain_by_id(chain_id)
    if not chain_data:
        raise HTTPException(status_code=404, detail="Chain not found")

    python_code = generate_code_for_chain(chain_data)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
        tmp_file.write(python_code.encode())
        tmp_file_path = tmp_file.name

    return FileResponse(tmp_file_path, filename="chain_code.py", media_type="application/octet-stream")
