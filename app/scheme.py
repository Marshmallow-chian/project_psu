from pydantic import BaseModel, validator, Field
from typing_extensions import Annotated
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone


class RequestCreateComment(BaseModel):
    postId: UUID
    parentId: Annotated[Optional[UUID], Field(nullable=True, default_factory=None)]
    nickname: Annotated[str, Field(max_length=100)] = 'nickname'
    message: Annotated[str, Field(max_length=993)] = 'massage'


class CommentsForComment(BaseModel):
    id: UUID
    message: str


class CommentResponse(BaseModel):
    id: UUID
    postId: UUID
    parentId: Annotated[Optional[UUID], Field(nullable=True, default_factory=None)]
    nickname: Annotated[str, Field(max_length=100, nullable=True)] = 'nickname'
    message: Annotated[str, Field(max_length=993, nullable=True)] = 'massage'
    createDate: datetime
    '''comments: CommentsForComment

    @validator('comments', pre=True, allow_reuse=True)
    def pony_set_to_list(cls, values):
        new_values = list()  # Добавляет всю инфу о продуктах
        for v in values:
            if hasattr(v, "to_dict"):
                new_values.append(v.to_dict())
        return new_values'''

    @validator("createDate")
    def parse_createDate(cls, createDate):
        return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    '''comment: CommentsForComment

    @validator('comment', pre=True, allow_reuse=True)
    def pony_set_to_list(cls, value):
        if hasattr(value, "to_dict"):
            value = value.to_dict()
        return value'''

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

    @validator("publishDate")
    def parse_publishDate(cls, publishDate):
        return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    class Config:
        orm_mode = True


class RequestUpdatePost(BaseModel):
    title: Annotated[Optional[str], Field(max_length=200, nullable=True)] = 'title'
    preview: Annotated[Optional[str], Field(max_length=2000, nullable=True)] = 'preview'
    body: Annotated[Optional[str], Field(max_length=20000, nullable=True)] = 'body'
    image: Annotated[Optional[str], Field(max_length=500, nullable=True)]


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
