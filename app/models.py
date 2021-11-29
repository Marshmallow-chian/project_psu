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
