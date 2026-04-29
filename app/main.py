from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.media import ensure_media_dirs
from app.api.v1.router import api_router
from fastapi.staticfiles import StaticFiles
from app.services.bootstrap_service import BootstrapService
from app.db.session import SessionLocal
from app.core.exceptions import rate_limit_handler
from app.services.cache import init_redis_pool, shutdown_redis_pool
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_media_dirs()

    async with SessionLocal() as session:
        await BootstrapService(session).ensure_admin_user()

    await init_redis_pool()
    yield
    await shutdown_redis_pool()
    print('hello')


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


app.state.limiter = settings.rate_limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# media/
ensure_media_dirs()
app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name='media')
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get('/health')
def health():
    return {'status': 'ok'}
