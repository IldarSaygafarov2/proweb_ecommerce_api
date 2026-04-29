from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_db, get_current_user
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.schemas.auth import UserCreate, UserRead, LoginData, TokenPair, RefreshRequest
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository
from app.models import User
from app.core.config import settings


router = APIRouter(
    tags=['Auth']
)


@router.get('/me', response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)


@router.post('/register', response_model=UserRead)
@settings.rate_limiter.limit('15/minute')
async def register(
        request: Request,
        payload: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    user = await AuthService(db).register(payload)  # User
    return UserRead.model_validate(user)


@router.post('/login', response_model=TokenPair)
@settings.rate_limiter.limit('15/minute')
async def login(
        request: Request,
        payload: LoginData,
        db: AsyncSession = Depends(get_db)
):
    return await AuthService(db).login(payload.email, payload.password)



@router.post('/token', response_model=TokenPair, summary="Token Endpoint")
@settings.rate_limiter.limit('15/minute')
async def token(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    return await AuthService(db).login(form_data.username, form_data.password)


@router.post('/refresh')
async def refresh(
        payload: RefreshRequest,
        db: AsyncSession = Depends(get_db)
):
    try:
        token_payload = decode_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if token_payload.get("type") != 'refresh':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')

    sub = token_payload.get('sub')
    if sub is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Token subject missing')

    user = await UserRepository(db).get_by_id(int(sub))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'User not found')

    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id))
    )

