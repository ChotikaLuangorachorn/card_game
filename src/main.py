from os import access

from fastapi import Depends, FastAPI
from .model.user import User
from .authentication import *
from .game import *

app = FastAPI()

@app.get('/')
async def root():
    return {'msg': 'Welcome to Card Game'}

def config_router():
    app.include_router(authentication_router)
    app.include_router(game_router)
config_router()

@app.get('/users/me', response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user