import os.path
import uvicorn
from pony.orm import db_session, commit
from models import db, User, Post, Comment
from scheme import (RequestCreateComment, RequestCreatePost, RequestUpdatePost, UserInDB)
from security.s_main import (get_current_active_user,
                             ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token)
from scheme import (UserResponse)
from security.s_scheme import Token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import FastAPI, Body, Depends, status, HTTPException, Query, Path
import os
from configuration.config import secret_key, author
from uuid import UUID


# использовать exception


app = FastAPI()
my_db = 'Comments_Post_User.sqlite'

SECRET_KEY = secret_key()
# print(uuid.uuid4())
"4328c48a-4dd1-4dac-beed-f681f7c208b1"


@app.on_event("startup")
async def start_app():
    """Выполняется при старте приложения"""
    # Прежде чем мы сможем сопоставить сущности с базой данных,
    # нам нужно подключиться, чтобы установить соединение с ней.
    # Это можно сделать с помощью метода bind()
    create_db = True
    '''if os.path.isfile(my_db):
        create_db = False'''
    db.bind(provider='sqlite', filename=my_db, create_db=create_db)
    db.generate_mapping(create_tables=create_db)
    AUTHOR = author()
    if create_db is True:
        with db_session:
            name = AUTHOR['nickname']
            print(name)
            print(User.get(nickname=name))
            print(User.exists(nickname=name))
            if not User.exists(nickname=AUTHOR['nickname']):
                User(**AUTHOR)
            commit()


# -----------------------------------------------------------------------------------------


@app.post("/api/v1/comments", tags=['Comments'])  # Максим
def creating_a_post(comment: RequestCreateComment = Body(...),
                    current_user: UserInDB = Depends(get_current_active_user)):
    return 'коммент создан'


@app.get("/api/v1/comments", tags=['Comments'])  # Никита
def get_comments_by_post(id_post: UUID):
    return 'коммент по посту'


@app.delete("/api/v1/comments/{id}", tags=['Comments'])  # Никита
def deleting_a_comment_by_id(id: UUID):
    return 'комент удалён'


# -----------------------------------------------------------------------------------------


@app.post("/api/v1/post", tags=['Post'])  # Максим
def creating_a_post(post: RequestCreatePost = Body(...)):
    return 'пост создан'


@app.get("/api/v1/post", tags=['Post'])  # Максим
def get_posts_by_pagination(page: int, count: int):
    return 'пост по странцие'


@app.get("/api/v1/post/search", tags=['Post'])  # Никита
def search_for_posts(searchData: str):
    return 'поиск'


@app.get("/api/v1/post/{id}", tags=['Post'])  # Никита
def get_post_by_id(id: UUID):
    return 'пост по id'


@app.put("/api/v1/post/{id}", tags=['Post'])  # Максим
def updating_a_post_by_id(id: UUID, post: RequestUpdatePost = Body(...)):
    return 'пост изменён'


@app.delete("/api/v1/post/{id}", tags=['Post'])  # Никита
def deleting_a_post_by_id(id: UUID):
    return 'пост удалён'


# ----------------------------------------------------------------------------------------------------


@app.post("/token", response_model=Token, tags=['User'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with db_session:
        name = form_data.username  # 'Zefirka'
        print(name)
        print(User.get(nickname=name))
        print(User.exists(nickname=name))
        user = authenticate_user(form_data.username, form_data.password)  # UserInDB or False
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 30 min
        access_token = create_access_token(data={"sub": user.nickname}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}


@app.get('/api/user', tags=['user'])
async def get_all_users():  # любой
    with db_session:
        users = User.get(nickname='Zefirka')
    return users


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
