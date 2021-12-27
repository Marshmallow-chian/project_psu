import os
from datetime import timedelta, datetime
from uuid import UUID
import pytz
import uvicorn
from fastapi import FastAPI, Body, Depends, status, HTTPException, Security
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordRequestForm
from pony.orm import db_session, commit
from starlette.types import Message
from app.scheme import (SuccessfulResponsePostInComments, SuccessfulResponseGetInComments, SuccessfulResponsePostInPost,
                        SuccessfulResponseGetInPost, SuccessfulResponsePutInPost,
                        Error422, Error403, Error404, Error401)
from app.scheme import (RequestCreateComment, CommentResponse, PostResponse, RequestCreatePost, RequestRegistration,
                        RequestUpdatePost, UserInDB)
from app.models import db, User, Post, Comment
from configuration.config import secret_key, author
from security.s_main import (get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user,
                             create_access_token, get_password_hash, get_current_active_user_for_comments)
from security.s_scheme import Token
from fastapi.security import OAuth2PasswordBearer


app = FastAPI()
my_db = 'Comments_Post_User.sqlite'

SECRET_KEY = secret_key()


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
            commit()


# -----------------------------------------------------------------------------------------


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    sch = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    for path in sch["paths"]:
        for method in sch["paths"][path]:
            if (dict_ := sch["paths"][path][method]["responses"]).get("422"):
                dict_['400'] = dict_.pop('422')
    app.openapi_schema = sch
    return app.openapi_schema


app.openapi = custom_openapi


# ------------------------------------------------------------------------------------------------------------------

# функция с комментарием должна иметь замочек, при не авторизованном пользователи она должа требовать никнейм,
# но длжен отсутсвовать заголовок авторизации, если авторизован, то выкидывать ошибку
# (авторизованный пользователь не должен передавать никнейм, взятие никнейма должно происходщить из токена)

# должна быть связь в бд между пользователем и коментарием, зарег пользователь должен иметь свои комментарии
# фиксировать что такого никнейма нет в бд

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/api/v1/comments",
          tags=['Comments'],
          responses={
              422: {"model": Error422, "description": "Invalid input data"},
              200: {"model": SuccessfulResponsePostInComments, "description": "Returns the id of the created post"},
              500: {"model": Message, "description": "Failed to create comment"}
          })
def creating_a_comment(comment: RequestCreateComment = Body(...),
                       current_user: UserInDB = Security(get_current_active_user_for_comments)):
    with db_session:
        request = comment.dict(exclude_unset=True, exclude_none=True)

        request['createDate'] = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
        request['post'] = comment.postId

# TODO: Никита, следующие 6 строчек нужно вставить в какое-то другое место этой функции
#  Условие должно проверять после проверки на наличие поста
        if current_user is not None:  # пользователь зарегестрирован
            request['nickname'] = current_user.nickname
            request['user'] = User.get(nickname=current_user.nickname)
        else:                         # пользователь не зарегестрирован
            request['nickname'] = comment.nickname
            request['user'] = None

        # try:
        if not Post.exists(id=request["postId"]):  # если пост не найден
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
        # except Exception:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to create comment",
        #     )


@app.get("/api/v1/comments", tags=['Comments'],
         responses={
             422: {"model": Error422, "description": "Invalid input data"},
             200: {"model": SuccessfulResponseGetInComments, "description": "Returns a list of comments"},
         })
def get_comments_by_post(postId: UUID):
    with db_session:
        try:
            if Comment.exists(postId=postId):
                comments = Comment.select()
                l_comments = []
                for i in comments:
                    if i.postId == postId:
                        l_comments.append(CommentResponse.from_orm(i))
                return l_comments
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found", )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid input data",
            )


@app.delete("/api/v1/comments/{id}", tags=['Comments'],
            responses={
                403: {"model": Error403, "description": "No access"},
                422: {"model": Error422, "description": "Invalid comment id"},
                200: {"model": Message, "description": "Returns the result success of execute"},
                500: {"model": Message, "description": "Failed to delete comment"}
            })
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
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete comment",
            )


# -----------------------------------------------------------------------------------------


@app.get("/dream", tags=['Ping'])
def ping():
    return 'Do you have a dream?'


@app.post("/api/v1/post", tags=['Post'],
          responses={
              403: {"model": Error403, "description": "No access"},
              422: {"model": Error422, "description": "Invalid comment id"},
              200: {"model": SuccessfulResponsePostInPost, "description": "Returns the id of the created post"},
              500: {"model": Message, "description": "Failed to create post"}
          })
async def creating_a_post(post: RequestCreatePost = Body(...), current_user: UserInDB = Security(get_current_active_user)):
    with db_session:
        try:
            post_ = post.dict()

            post_['publishDate'] = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
            post_['author'] = User.get(nickname=current_user.nickname)

            new_post = Post(**post_)
            commit()
            return new_post.id
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create post",
            )


@app.get("/api/v1/post", tags=['Post'],
         responses={
             422: {"model": Error422, "description": "Invalid input data"},
             200: {"model": SuccessfulResponseGetInPost, "description": "Returns a list of posts"},
         })
def get_posts_by_pagination(page: int, count: int):
    with db_session:
        posts = Post.select()[::]
        if len(posts) >= (page - 1) * count:
            return posts[(page - 1) * count].to_dict()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data",
            )


@app.get("/api/v1/post/search", tags=['Post'],
         responses={
             422: {"model": Error422, "description": "Invalid input data"},
             200: {"model": SuccessfulResponseGetInPost, "description": "Returns a list of found posts"},
         })
async def search_for_posts(searchData: str):
    with db_session:
        try:
            response = Post.select(
                lambda p: searchData.lower() in p.title.lower() or searchData.lower() in p.body.lower())
            all_response = []
            for i in response:
                all_response.append(PostResponse.from_orm(i))
            if all_response == []:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Data not found",
                )
            return all_response
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post",
            )


@app.get("/api/v1/post/{id}", tags=['Post'],
         responses={
             422: {"model": Error422, "description": "Invalid input data"},
             404: {"model": Error404, "description": "Not fount post by id"},
             200: {"model": SuccessfulResponseGetInPost, "description": "Returns a post find by id"},
         })
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
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data",
            )


@app.put("/api/v1/post/{id}", tags=['Post'],
         responses={
             403: {"model": Error403, "description": "No access"},
             422: {"model": Error422, "description": "Invalid input id"},
             200: {"model": SuccessfulResponsePutInPost, "description": "Returns updated post"},
             500: {"model": Message, "description": "Failed to update post"}
         })
def updating_a_post_by_id(id: UUID, edit_pr: RequestUpdatePost = Body(...),
                          current_user: UserInDB = Security(get_current_active_user)):
    with db_session:
        try:
            if Post.exists(id=id):
                product_chng = edit_pr.dict(exclude_unset=True, exclude_none=True)
                Post[id].set(**product_chng)
                commit()
                return PostResponse.from_orm(Post[id])
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Data not found",
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update post",
            )


@app.delete("/api/v1/post/{id}", tags=['Post'],
            responses={
                403: {"model": Error403, "description": "No access"},
                422: {"model": Error422, "description": "Invalid post id"},
                200: {"model": Message, "description": "Returns the result success of execute"},
                500: {"model": Message, "description": "Failed to delete post"}
            })
def deleting_a_post_by_id(id: UUID, current_user: UserInDB = Security(get_current_active_user)):
    with db_session:
        try:
            if Post.exists(id=id):
                Post[id].delete()
                commit()
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found",
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete post",
            )


# ----------------------------------------------------------------------------------------------------


@app.post("/api/v1/user/auth", response_model=Token, tags=['User'],
          responses={
              401: {"model": Error401, "description": "Unauthorized"},
              422: {"model": Error422, "description": "Invalid input data"},
              200: {"model": Message, "description": "Returns the authentication token"},
          })
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
        except Exception as e:
            return e


@app.post('/api/v1/user/reg', tags=['User'],
          responses={
              401: {"model": Error401, "description": "Unauthorized"},
              422: {"model": Error422, "description": "Invalid input data"},
              200: {"model": Message, "description": "Returns the authentication token"},
          })
async def account_registration(user: RequestRegistration = Body(...)):  # любой
    with db_session:
        try:
            n_user = user.dict()
            print(User.exists(nickname=user.nickname))
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
        except Exception as e:
            return e

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
