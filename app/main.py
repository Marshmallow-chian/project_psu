import os.path
import uvicorn
from pony.orm import db_session, commit
from app.models import db, User, Post, Comment
from app.scheme import (RequestCreateComment, RequestCreatePost, RequestUpdatePost)
from security.s_main import (get_password_hash, get_current_active_user,
                             ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token)
from app.scheme import (UserResponse)
from security.s_scheme import Token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, Body, Security, Depends, status, HTTPException, Query, Path
import os
from configuration.config import secret_key, author

# использовать exception
# TODO: как выглядят id
# TODO: add (Query)
# TODO: add поле Authorization
# TODO: Авторизация User OAuth2PasswordRequestForm -> RequestAuthorize


app = FastAPI()
my_db = 'Manufacturer_and_Products.sqlite'

SECRET_KEY = None


@app.on_event("startup")
async def start_app():
    global SECRET_KEY
    """Выполняется при старте приложения"""
    # Прежде чем мы сможем сопоставить сущности с базой данных,
    # нам нужно подключиться, чтобы установить соединение с ней.
    # Это можно сделать с помощью метода bind()
    create_db = True
    if os.path.isfile(my_db):
        create_db = False
    SECRET_KEY = secret_key()
    db.bind(provider='sqlite', filename=my_db, create_db=create_db)
    db.generate_mapping(create_tables=create_db)
    AUTHOR = author()
    if create_db is True:
        with db_session:
            if not User.exists(nickname=AUTHOR['nickname']):
                User(**AUTHOR)
            commit()


# -----------------------------------------------------------------------------------------


@app.post("/api/v1/comments", response_model=Token, tags=['Comments'])
def creating_a_post(comment: RequestCreateComment = Body(...)):
    pass


@app.get("/api/v1/comments", response_model=Token, tags=['Comments'])
def get_comments_by_post(id_post: str):
    pass


@app.delete("/api/v1/comments/{id}", response_model=Token, tags=['Comments'])
def deleting_a_comment_by_id(id: str):
    pass


# -----------------------------------------------------------------------------------------


@app.post("/api/v1/post", response_model=Token, tags=['Post'])
def creating_a_post(post: RequestCreatePost = Body(...)):
    pass


@app.get("/api/v1/post", response_model=Token, tags=['Post'])
def get_posts_by_pagination(page: int, count: int):
    pass


@app.get("/api/v1/post/search", response_model=Token, tags=['Post'])
def search_for_posts(searchData: str, ):
    pass


@app.get("/api/v1/post/{id}", response_model=Token, tags=['Post'])
def get_post_by_id(id: str):
    pass


@app.put("/api/v1/post/{id}", response_model=Token, tags=['Post'])
def updating_a_post_by_id(id: str, post: RequestUpdatePost = Body(...)):
    pass


@app.delete("/api/v1/post/{id}", response_model=Token, tags=['Post'])
def deleting_a_post_by_id(id: str):
    pass


# ----------------------------------------------------------------------------------------------------


@app.post("/api/v1/user/auth", response_model=Token, tags=['User'])
async def authorize_in_account(form_data: OAuth2PasswordRequestForm = Depends()):
    with db_session:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if len(form_data.scopes) != 1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 30 min
        access_token = create_access_token(data={"sub": user.nickname, "scopes": form_data.scopes},
                                           expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
