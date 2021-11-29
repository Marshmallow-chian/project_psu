from pydantic import BaseModel, validator, Field
from typing_extensions import Annotated
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
import pytz


class RequestCreateComment(BaseModel):
    postId: UUID
    parentId: Annotated[Optional[UUID], Field(nullable=True, default_factory=None)]
    nickname: Annotated[str, Field(max_length=100, example='nickname')]
    message: Annotated[str, Field(max_length=993, example='massage')]


class CommentResponse(BaseModel):
    id: UUID
    postId: UUID
    parentId: Annotated[Optional[UUID], Field(nullable=True, default_factory=None)]
    nickname: Annotated[str, Field(max_length=100, nullable=True)] = 'nickname'
    message: Annotated[str, Field(max_length=993, nullable=True)] = 'massage'
    createDate: datetime

    @validator("createDate")
    def parse_createDate(cls, createDate):
        return datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')


    class Config:
        orm_mode = True


class RequestCreatePost(BaseModel):
    title: Annotated[str, Field(max_length=200, example='title')]
    preview: Annotated[str, Field(max_length=2000, example='preview')]
    body: Annotated[str, Field(max_length=20000, example='body')]
    image: Annotated[str, Field(max_length=500, example='image')]


class PostResponse(BaseModel):
    id: UUID
    title: Annotated[str, Field(nullable=True)] = 'title'
    preview: Annotated[str, Field(nullable=True)] = 'preview'
    body: Annotated[str, Field(nullable=True)] = 'body'
    image: Annotated[str, Field(max_length=500, nullable=True)]
    publishDate: datetime

    @validator("publishDate")
    def parse_publishDate(cls, publishDate):
        return datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')

    class Config:
        orm_mode = True


class RequestUpdatePost(BaseModel):
    title: Annotated[Optional[str], Field(max_length=200, nullable=True)] = 'title'
    preview: Annotated[Optional[str], Field(max_length=2000, nullable=True)] = 'preview'
    body: Annotated[Optional[str], Field(max_length=20000, nullable=True)] = 'body'
    image: Annotated[Optional[str], Field(max_length=500, nullable=True)]


class RequestAuthorize(BaseModel):
    nickname: Annotated[str, Field(max_length=100, example='nickname')]
    password: Annotated[str, Field(max_length=255, example='password')]


class RequestRegistration(BaseModel):
    nickname: Annotated[str, Field(max_length=100, example='nickname')]
    password: Annotated[str, Field(max_length=255, example='password')]


class UserResponse(BaseModel):
    id: UUID
    nickname: Annotated[str, Field(max_length=255, example='nickname')]

    class Config:
        orm_mode = True


class UserInDB(UserResponse):
    hashed_password: str
