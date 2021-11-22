import uvicorn
from pony.orm import db_session, commit
from app.models import db, User, Post, Comment
from app.scheme import (RequestCreateComment, CommentResponse, PostResponse, RequestCreatePost, RequestRegistration,
                        RequestUpdatePost,
                        UserInDB)
from security.s_main import (get_current_active_user,
                             ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_password_hash)
from app.scheme import (UserResponse)
from security.s_scheme import Token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, Body, Depends, status, HTTPException, Security
from configuration.config import secret_key, author
from uuid import UUID
from datetime import datetime
from jose import JWTError
import os

app = FastAPI()
my_db = 'Comments_Post_User.sqlite'

SECRET_KEY = secret_key()

"4328c48a-4dd1-4dac-beed-f681f7c208b1"


@app.on_event("startup")
async def start_app():
    """Выполняется при старте приложения"""
    # Прежде чем мы сможем сопоставить сущности с базой данных,
    # нам нужно подключиться, чтобы установить соединение с ней.
    # Это можно сделать с помощью метода bind()
    create_db = True
    if os.path.isfile(my_db):
        create_db = False
    db.bind(provider='sqlite', filename=my_db, create_db=create_db)
    db.generate_mapping(create_tables=create_db)
    AUTHOR = author()
    if create_db is True:
        with db_session:
            name = AUTHOR['nickname']
            if not User.exists(nickname=AUTHOR['nickname']):
                User(**AUTHOR)
            if not User.exists(id=UUID('1a984747-07e7-4f6c-a96f-f01adec705bf')):
                User(id=UUID('1a984747-07e7-4f6c-a96f-f01adec705bf'), nickname='User1',
                     hashed_password=get_password_hash('123'))
            commit()


# -----------------------------------------------------------------------------------------


@app.post("/api/v1/comments", tags=['Comments'])
def creating_a_comment(comment: RequestCreateComment = Body(...)):
    with db_session:
        request = comment.dict(exclude_unset=True, exclude_none=True)
        request['createDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        request['post'] = comment.postId

        try:
            if not Post.exists(id=request["postId"]):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found",
                )
            elif request.get('parentId') is not None:  # ответ на комментарий
                if not Comment.exists(id=request['parentId']):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Invalid input data",
                    )
                request['comment'] = comment.parentId
                comment = Comment(**request)
                commit()
                return CommentResponse.from_orm(comment)

            comment = Comment(**request)
            commit()
            return CommentResponse.from_orm(comment)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment",
            )


@app.get("/api/v1/get_comments", tags=['Comments'])  # потом удалить
def get_all_comment(id: UUID):
    with db_session:
        posts = Comment.get(id=id)
        return CommentResponse.from_orm(posts)


@app.get("/api/v1/comments", tags=['Comments'])
def get_comments_by_post(id_post: UUID):
    with db_session:
        try:
            if Post.exists(id=id_post):
                post = Post.get(id=id_post)
                return post.comments
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input data",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid input data",
            )


@app.delete("/api/v1/comments/{id}", tags=['Comments'])
def deleting_a_comment_by_id(id: UUID, current_user: UserInDB = Security(get_current_active_user)):
    with db_session:
        try:
            if Comment.exists(id=id):
                Comment[id].delete()
                commit()
                return True
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid comment id",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment",
            )


# -----------------------------------------------------------------------------------------


@app.post("/api/v1/post", tags=['Post'])
def creating_a_post(post: RequestCreatePost = Body(...), current_user: UserInDB = Security(get_current_active_user)):
    with db_session:
        try:
            post_ = post.dict()
            post_['publishDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            post_['author'] = User.get(nickname=current_user.nickname)
            new_post = Post(**post_)
            commit()
            return new_post.id
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create post",
                headers={"WWW-Authenticate": "Bearer"},
            )


# TODO: реализовать валидацию автора и поста через pydantic.
#  Сделать отдельную модель для выхода OutProduct и модель для базы данных.


@app.get("/api/v1/post", tags=['Post'])
def get_posts_by_pagination(page: int, count: int):
    try:
        posts = Post.select()[::-1]
        return posts[(page - 1) * count]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data",
        )


@app.get("/api/v1/get_post", tags=['Post'])  # потом удалить
def get_all_posts():
    with db_session:
        posts = Post.select()
        # преобразуем запрос в SQL, а затем отправим в базу данных
        all_posts = []
        for i in posts:
            all_posts.append(PostResponse.from_orm(i))
    return all_posts


@app.get("/api/v1/post/search", tags=['Post'])
async def search_for_posts(searchData: str):
    with db_session:
        response = Post.select(lambda p: searchData in p.title or searchData in p.body)
        all_response = []
        try:
            for i in response:
                all_response.append(PostResponse.from_orm(i))
            if all_response == []:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Data not found",
                )
            return all_response
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post",
            )


@app.get("/api/v1/post/{id}", tags=['Post'])
def get_post_by_id(id: UUID):
    with db_session:
        try:
            if Post.exists(id=id):
                products = Post.get(id=id)
                return PostResponse.from_orm(products)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Not found post by id",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data",
            )


@app.put("/api/v1/post/{id}", tags=['Post'])
def updating_a_post_by_id(id: UUID, edit_pr: RequestUpdatePost = Body(...),
                          current_user: UserInDB = Security(get_current_active_user)):
    with db_session:
        try:
            if Post.exists(id=id):
                product_chng = edit_pr.dict(exclude_unset=True, exclude_none=True)
                Post[id].set(**product_chng)
                commit()
                return (PostResponse.from_orm(Post[id]))
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Data not found",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update post",
                headers={"WWW-Authenticate": "Bearer"},
            )


@app.delete("/api/v1/post/{id}", tags=['Post'])
def deleting_a_post_by_id(id: UUID, current_user: UserInDB = Security(get_current_active_user)):
    with db_session:
        try:
            if Post.exists(id=id):
                Post[id].delete()
                commit()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid post id",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete post",
            )


# ----------------------------------------------------------------------------------------------------


@app.post("/api/v1/user/auth", response_model=Token, tags=['User'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with db_session:
        try:
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
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data",
            )


@app.post('/api/v1/user/reg', tags=['User'])
async def account_registration(user: RequestRegistration = Body(...)):  # любой
    with db_session:
        try:
            n_user = user.dict()
            if User.exists(nickname=user.nickname):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this nickname already exists",
                )
            user_ = {'nickname': n_user['nickname'], 'hashed_password': get_password_hash(n_user['password'])}
            User(**user_)
            commit()
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 30 min
            access_token = create_access_token(data={"sub": user_['nickname']}, expires_delta=access_token_expires)
            return access_token
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create account",
            )


@app.get('/api/user', tags=['User'])
async def get_all_users():  # любой
    with db_session:
        users = User.select()  # преобразуем запрос в SQL, а затем отправим в базу данных4
        all_users = []
        for i in users:
            all_users.append(UserResponse.from_orm(i))
    return all_users


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
