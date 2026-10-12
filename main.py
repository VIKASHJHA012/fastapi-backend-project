from fastapi import FastAPI,Request
from routes.users import router as user_router
from routes.auth import router as auth_router
from routes.posts import router as post_router
from routes.tag import router as tag_router
from routes.posttag import router as posttag_router
from fastapi.responses import JSONResponse
from database import init_db
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import time


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    yield
app = FastAPI(lifespan= lifespan)

@app.middleware("http")
async def measure_request_time(request : Request,call_next):
    start_time = time.perf_counter()

    response = await call_next(request)
    duration  = time.perf_counter() - start_time

    logger.info("%s %s completed in  %.4f seconds",request.method,request.url.path,duration)

    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)   

@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    logger.exception(
        "Unexpected error occured while processing %s %s",
        request.method,
        request.url.path,
        exc_info= (type(exc),exc,exc.__traceback__)
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


app.include_router(user_router,prefix="/api-version-v1")
app.include_router(auth_router,prefix="/api-registeration-v1")
app.include_router(post_router,prefix="/api-post-v1")
app.include_router(posttag_router,prefix="/api-post_tag-v1")
app.include_router(tag_router,prefix="/api-tag_router-v1")