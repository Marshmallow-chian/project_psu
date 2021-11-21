from pydantic import BaseModel, validator, Field
from typing_extensions import Annotated
from uuid import UUID
from datetime import datetime


class RequestCreateComment(BaseModel):
    postId: UUID
    parentId: UUID
    nickname: Annotated[str, Field(max_length=100)] = 'nickname'
    message:  Annotated[str, Field(max_length=993)] = 'massage'


class PostIdForCommentsResponse(BaseModel):
    id: UUID


class CommentResponse(BaseModel):
    id: UUID
    postId: PostIdForCommentsResponse
    parentId: Annotated[UUID, Field(default_factory=None)]  # комментарий родитель (тот кому ответили) null - комент первого уровня
    nickname: Annotated[str, Field(max_length=100, nullable=True)] = 'nickname'
    message: Annotated[str, Field(max_length=993, nullable=True)] = 'massage'
    createDate: datetime

    @validator('postId', pre=True, allow_reuse=True)
    def pony_set_to_list(cls, value):
        if hasattr(value, "to_dict"):
            value = value.to_dict()
        return value


    class Config:
        orm_mode = True


class RequestCreatePost(BaseModel):
    title: Annotated[str, Field(max_length=200)] = 'title for'
    preview: Annotated[str, Field(max_length=2000)] = 'preview'
    body: Annotated[str, Field(max_length=20000)] = 'body'


class PostResponse(BaseModel):
    title: Annotated[str, Field(nullable=True)] = 'title'
    preview: Annotated[str, Field(nullable=True)] = 'preview'
    body: Annotated[str, Field(nullable=True)] = 'body'
    publishDate: datetime

    class Config:
        orm_mode = True


class RequestUpdatePost(BaseModel):
    title: Annotated[str, Field(max_length=200)] = 'title'
    preview: Annotated[str, Field(max_length=2000)] = 'preview'
    body: Annotated[str, Field(max_length=20000)] = 'body'


class RequestAuthorize(BaseModel):
    nickname: Annotated[str, Field(max_length=255)] = 'nickname'
    password:  Annotated[str, Field(max_length=255)] = 'password'


class UserResponse(BaseModel):
    # используется для вывода имени пользователя, после его регистрации
    nickname: Annotated[str, Field(max_length=255)] = 'nickname'

    class Config:
        orm_mode = True


class UserInDB(UserResponse):
    hashed_password: str

