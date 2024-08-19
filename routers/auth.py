from datetime import timedelta
import secrets
from authlib.integrations.starlette_client import OAuth,OAuthError
from fastapi import APIRouter, Depends, HTTPException,Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from authlib.oauth2.rfc6749 import OAuth2Token
from models import Users
from .validators import CreateUserRequest, GoogleUser, Token, RefreshTokenRequest
from .services import (
    create_access_token, authenticate_user, bcrypt_context, create_refresh_token,
    create_user_from_google_info, get_user_by_google_sub, token_expired, decode_token, user_dependency
)
from database import db_dependency
from starlette import status
import logging

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

GOOGLE_CLIENT_ID = "940039925996-dme45jmum3u5870lsslhb7d10vr8uef5.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/callback/google"
FRONTEND_URL = "http://localhost:3000"

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@router.get("/google")
async def login_google(request: Request):
    state = secrets.token_urlsafe()
    logging.debug(f"CSRF Warning! State mismatch: stored_state={state},")
    request.session['oauth_state'] = state
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback/google")
async def auth_google(request: Request, db: db_dependency):
    stored_state = request.session.get('oauth_state')
    received_state = request.query_params.get('state')
    
    # Verify state
    # if stored_state != received_state:
    logging.error(f"CSRF Warning! State mismatch: stored_state={stored_state}, received_state={received_state}")
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSRF token mismatch")
    try:
        token: OAuth2Token = await oauth.google.authorize_access_token(request)
        logging.info(f"Token received: {token}")
        
        user_info = token.get("userinfo")
        logging.info(f"User info: {user_info}")

        google_user = GoogleUser(**user_info)
        
        existing_user = get_user_by_google_sub(google_user.sub, db)
        logging.info(f"Existing user: {existing_user}")

        if existing_user:
            user = existing_user
        else:
            user = create_user_from_google_info(google_user, db)
        
        logging.info(f"User: {user}")

        access_token = create_access_token(user.username, user.id, timedelta(days=7))
        refresh_token = create_refresh_token(user.username, user.id, timedelta(days=14))
        logging.info(f"Access token: {access_token}")
        logging.info(f"Refresh token: {refresh_token}")

        return RedirectResponse(f"{FRONTEND_URL}/auth?access_token={access_token}&refresh_token={refresh_token}")
    except OAuthError as e:
        logging.error(f"OAuthError: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        password_hash=bcrypt_context.hash(create_user_request.password),
        role_id=create_user_request.role_id,
        email=create_user_request.email
    )
    db.add(create_user_model)
    db.commit()
    return create_user_request

@router.get("/get-user", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency):
    return user

@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
    
    access_token = create_access_token(user.username, user.id, timedelta(days=7))
    refresh_token = create_refresh_token(user.username, user.id, timedelta(days=14))
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(db: db_dependency, refresh_token_request: RefreshTokenRequest):
    token = refresh_token_request.refresh_token
    if token_expired(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is expired.")
    
    user = decode_token(token)
    access_token = create_access_token(user["sub"], user["id"], timedelta(days=7))
    refresh_token = create_refresh_token(user["sub"], user["id"], timedelta(days=14))
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
