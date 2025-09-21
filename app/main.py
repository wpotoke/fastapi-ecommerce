# pylint:disable=broad-exception-caught
import sys
import time
from uuid import uuid4

# from datetime import datetime, timedelta, timezone
from celery import Celery

# from celery.schedules import crontab
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import categories, products, users, reviews
from app.task import call_background_task


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
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
    broker_connection_retry_on_startup=True,
)

app = FastAPI(
    title="FastAPI ecommerce - Интеренет магазин",
    version="0.1.0",
)


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

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)


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
