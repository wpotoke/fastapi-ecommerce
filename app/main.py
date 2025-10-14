# pylint:disable=broad-exception-caught
import os
import sys
import time
from uuid import uuid4
from typing import Annotated
import aiofiles

# from datetime import datetime, timedelta, timezone
from celery import Celery

# from celery.schedules import crontab
from loguru import logger
from fastapi import FastAPI, Request, File, UploadFile, HTTPException, status, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from app.api import category_router, product_router, review_router, user_router
from app.task import call_background_task
from app.core.config import settings


if not os.path.exists("app/files/avatars"):
    os.makedirs("app/files/avatars")

logger.add(
    sys.stdout,
    colorize=True,
    format="<green>Log:</green> [{extra[log_id]}:"
    "{time} - <magenta>{level} - <CYAN>{message}</CYAN></magenta>]",
    level="INFO",
    enqueue=True,
)

celery = Celery(
    __name__,
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    broker_connection_retry_on_startup=True,
)

app = FastAPI(
    title="FastAPI ecommerce - Интеренет магазин",
    version="0.1.0",
)


app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = uuid4()
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                print(request.path_params)
                logger.info("Successfully accessed: url-path" + request.url.path)
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response


allow_origins = ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"Request duration: {duration:.10f} seconds")
    return response


# app.add_middleware(TrustedHostMiddleware, allow_hosts=["http://127.0.0.1:8000"])
# app.add_middleware(HTTPSRedirectMiddleware)

app.include_router(category_router)
app.include_router(product_router)
app.include_router(review_router)
app.include_router(user_router)


@app.get("/")
async def root(message):
    """Корневой маршрут, подверждающий, что API работает."""
    # task_datetime = datetime.now(timezone.utc) + timedelta(minutes=1)
    call_background_task.apply_async(args=[message], expires=3600)
    return {"message": "Добро пожаловать в API интернет-магазина!"}


celery.conf.beat_schedule = {
    "run-me-background-task": {
        "task": "app.task.call_background_task",
        "schedule": 60.0,
        "args": ("Test text message",),
    }
}


@app.post("/uploadfile_async_save")
async def create_upload_file_async_save(files: list[UploadFile] = File(...)):

    response_info = []

    for file in files:

        filename_lower = file.filename.lower()
        file_ext = os.path.splitext(filename_lower)[1]

        if file.content_type not in settings.ALLOWED_IMAGE_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: '{file.content_type}.'"
                f"Only {', '.join(settings.ALLOWED_IMAGE_MIME_TYPES)} are allowed.",
            )

        if file_ext not in settings.ALLOWED_FILE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension: '{file_ext}'. "
                f"Only {', '.join(settings.ALLOWED_FILE_EXTENSIONS)} are allowed.",
            )

        file_location = f"app/files/avatars/{file.filename}"
        try:
            async with aiofiles.open(file_location, "wb") as out_file:
                chunk_size = 1024 * 1024
                current_size = 0
                while content := await file.read(chunk_size):
                    current_size += len(content)
                    if current_size > settings.MAX_FILE_SIZE_BYTES:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File too large. Max size is {settings.MAX_FILE_SIZE_MB}MB.",
                        )
                    await out_file.write(content)
            response_info.append(
                {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size_bytes": current_size,
                    "status": "File uploaded and size validated successfully.",
                }
            )
        except HTTPException as e:
            if os.path.exists(file_location):
                os.remove(file_location)
            response_info.append(
                {
                    "filename": file.filename,
                    "status": "error",
                    "message": f"Could not save file: {e}",
                }
            )
        except Exception as e:
            # Общая обработка других возможных ошибок (например, проблем с диском)
            if os.path.exists(file_location):
                os.remove(file_location)  # Удаляем неполный файл
            response_info.append(
                {
                    "filename": file.filename,
                    "status": "error",
                    "message": f"An unexpected error occurred during file upload: {e}",
                }
            )
        finally:
            await file.close()

    return {"uploaded_files": response_info}


@app.get("/download/{file_name}", response_class=FileResponse)
async def download_file(file_name: Annotated[str, Path(...)]):
    file_path = os.path.join("app/files/avatars/", file_name)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found."
        )
    return FileResponse(path=file_path, filename=file_name)


async def file_streamer(file_path: str, chunk_size: int = 8192):
    try:
        async with aiofiles.open(file_path, mode="rb") as file:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")


@app.get("/stream-large-file/{file_name}")
async def stream_large_file(file_name: str):
    file_path = os.path.join("app/files/", file_name)
    if not os.path.exists(file_path):
        return {
            "error": f"File '{file_path}' not found on server. Please restart the application."
        }
    return StreamingResponse(
        file_streamer(file_path), media_type="application/octet-stream"
    )
