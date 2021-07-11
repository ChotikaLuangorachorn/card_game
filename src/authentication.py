from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import users_db
from .model.user import User, UserInDB
from .model.token import Token, TokenData
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# -------------------- variable --------------------
SECRET_KEY = '9879480a4ca233b8e8764bfd9ce05909ca9dc31836e49a9feb573b6e8aaf2519'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

authentication_router = APIRouter(
    prefix='',
    tags = ['authentication'],
    responses = {status.HTTP_404_NOT_FOUND: {'message': 'Not found'}}
)
pwd_context = CryptContext(schemes=['bcrypt'])
oauth2_schema = OAuth2PasswordBearer(tokenUrl='token')

# -------------------- function --------------------
def get_user_info(db, username: str):
    if username in db:
        user_info = db[username]
        return UserInDB(**user_info)
    else:
        return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db, username: str, password: str):
    user = get_user_info(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_schema)):

    credentails_exception = HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = 'Could not validate creditails',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        if username is None:
            raise credentails_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentails_exception

    user = get_user_info(users_db, username=token_data.username)
    if user is None:
        raise credentails_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

# -------------------- router --------------------
@authentication_router.post('/token', response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}

# -------------------- unused code --------------------
def get_password_hash(password):
    return pwd_context.hash(password)