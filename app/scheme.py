from pydantic import BaseModel, validator, Field
from typing import Annotated
from uuid import UUID
from datetime import datetime


class RequestCreateComment(BaseModel):
    postId: UUID
    parentId: Annotated[UUID, Field(nullable=True)]
    nickname: Annotated[str, Field(max_length=100)] = 'nickname'
    message: Annotated[str, Field(max_length=993)] = 'massage'


class CommentResponse(BaseModel):
    id: UUID
    postId: UUID
    parentId: Annotated[UUID, Field(nullable=True)]
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
    image: Annotated[str, Field(max_length=500)]


class PostResponse(BaseModel):
    id: UUID
    title: Annotated[str, Field(nullable=True)] = 'title'
    preview: Annotated[str, Field(nullable=True)] = 'preview'
    body: Annotated[str, Field(nullable=True)] = 'body'
    image: Annotated[str, Field(max_length=500, nullable=True)]
    publishDate: datetime

    class Config:
        orm_mode = True


class RequestUpdatePost(BaseModel):
    title: Annotated[str, Field(max_length=200, nullable=True)] = 'title'
    preview: Annotated[str, Field(max_length=2000, nullable=True)] = 'preview'
    body: Annotated[str, Field(max_length=20000, nullable=True)] = 'body'
    image: Annotated[str, Field(max_length=500, nullable=True)]


class RequestAuthorize(BaseModel):
    nickname: Annotated[str, Field(max_length=100)] = 'nickname'
    password: Annotated[str, Field(max_length=255)] = 'password'


class RequestRegistration(BaseModel):
    nickname: Annotated[str, Field(max_length=100)] = 'nickname'
    password: Annotated[str, Field(max_length=255)] = 'password'


class UserResponse(BaseModel):
    id: UUID
    nickname: Annotated[str, Field(max_length=255)] = 'nickname'

    class Config:
        orm_mode = True


class UserInDB(UserResponse):
    hashed_password: str
