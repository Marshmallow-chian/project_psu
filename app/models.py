from datetime import datetime
from uuid import UUID, uuid4
from pony.orm import *

db = Database()


class User(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    nickname = Required(str, 255, unique=True)
    hashed_password = Optional(str)
    posts = Set('Post')


class Post(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    title = Optional(str, 200)
    preview = Optional(str, 2000)
    body = Optional(str, 20000)
    publishDate = Optional(datetime)
    author = Required(User)
    comments = Set('Comment')


class Comment(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    postId = Required(UUID)
    parentId = Required(UUID, unique=True)  # id комментария
    nickname = Required(str, 100)
    message = Required(str, 993)
    createDate = Required(datetime, precision=0, default=lambda: datetime.now())
    post = Required(Post)
