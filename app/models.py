from datetime import datetime
from uuid import UUID, uuid4
from pony.orm import *
from pydantic import BaseModel

db = Database()


class User(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    nickname = Required(str, 255, unique=True)
    hashed_password = Optional(str)
    posts = Set('Post')


class Post(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    title = Required(str, 200)
    preview = Required(str, 2000)
    body = Required(str, 20000)
    image = Optional(str, 500)
    publishDate = Required(datetime)
    author = Required(User)
    comments = Set('Comment')


class Comment(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    postId = Required(UUID)
    parentId = Optional(UUID)  # id комментария
    nickname = Required(str, 100)
    message = Required(str, 993)
    createDate = Optional(datetime)
    post = Required(Post)
    comments = Set('Comment', reverse='comment')
    comment = Optional('Comment', reverse='comments')


# ----------------------------------------------------------------------------------------------------------------------

class Error422(BaseModel):
    type: str
    title: str
    detail: str
    status: int
    instance: str
    additionalProp1: str
    additionalProp2: str
    additionalProp3: str


class Error401(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    additionalProp1: str
    additionalProp2: str
    additionalProp3: str


class Error403(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    additionalProp1: str
    additionalProp2: str
    additionalProp3: str


class Error404(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    additionalProp1: str
    additionalProp2: str
    additionalProp3: str


# ----------------------------------------------------------------------------------------------------------------------

class SuccessfulResponsePostInComments(BaseModel):
    id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    postId = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    parentId = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    nickname = "string"
    message = "string"
    createDate = "2021-11-28T15:37:38.017Z"


class SuccessfulResponseGetInComments(BaseModel):
    id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    postId = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    parentId = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    nickname = "string"
    message = "string"
    createDate = "2021-11-28T153738.017Z"


class SuccessfulResponseGetInPost(BaseModel):
    id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    title = "string"
    preview = "string"
    body = "string"
    publishDate = "2021-11-28T16:46:13.140Z"


class SuccessfulResponsePutInPost(BaseModel):
    id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    title = "string"
    preview = "string"
    body = "string"
    publishDate = "2021-11-28T16:46:13.140Z"


class SuccessfulResponsePostInPost(BaseModel):
    id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
