import os.path
import uuid

import uvicorn
from pony.orm import db_session, commit
from app.models import db, User, Post, Comment
from app.scheme import (RequestCreateComment, PostResponse, RequestCreatePost, RequestUpdatePost, UserInDB)
from security.s_main import (get_current_active_user,
                             ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_password_hash)
from scheme import (UserResponse)
from security.s_scheme import Token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import FastAPI, Body, Depends, status, HTTPException, Query, Path
import os
from configuration.config import secret_key, author
from uuid import UUID, uuid4
from datetime import datetime

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
            if not User.exists(nickname=AUTHOR['nickname']):
                User(**AUTHOR)
            if not User.exists(id=UUID('1a984747-07e7-4f6c-a96f-f01adec705bf')):
                User(id=UUID('1a984747-07e7-4f6c-a96f-f01adec705bf'), nickname='User1', hashed_password=get_password_hash('123'))

            commit()


# -----------------------------------------------------------------------------------------


@app.post("/api/v1/comments", tags=['Comments'])  # Никита
def creating_a_comment(comment: RequestCreateComment = Body(...)):
    with db_session:
        return 'коммент создан'


@app.get("/api/v1/comments", tags=['Comments'])  # Настя
def get_comments_by_post(id_post: UUID):
    with db_session:
        if Post.exists(id=id_post):
            post = Post.get(id=id_post)
            return post.comments
        else:
            return 'товара с таким id не существует'



@app.delete("/api/v1/comments/{id}", tags=['Comments'])  # Настя
def deleting_a_comment_by_id(id: UUID):
    with db_session:
        if Comment.exists(id=id):
            Comment[id].delete()
            commit()
            return "Комментарий удалён"
        return "Комментарий не найден"


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


@app.delete("/api/v1/post/{id}", tags=['Post'])  # Настя
def deleting_a_post_by_id(id: UUID):
    with db_session:
        if Post.exists(id=id):
            Post[id].delete()
            commit()
            return "Пост удалён"
        return "Пост не найден"


# ----------------------------------------------------------------------------------------------------


@app.post("/token", response_model=Token, tags=['User'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with db_session:
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


@app.get('/api/user', tags=['User'])
async def get_all_users(current_user: UserInDB = Depends(get_current_active_user)):  # любой
    with db_session:
        print(current_user)
        user = User.get(nickname=current_user.nickname)
        print(f'User: {user}')
        users = User.select()  # преобразуем запрос в SQL, а затем отправим в базу данных4
        all_users = []
        for i in users:
            all_users.append(UserResponse.from_orm(i))
    return all_users


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
