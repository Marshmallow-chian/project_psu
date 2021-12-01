from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

def author():
    from security.s_main import get_password_hash

    author_login = os.getenv("AUTHOR_LOGIN")
    author_hashed_password = get_password_hash(os.getenv("AUTHOR_PASSWORD"))
    _author = {'nickname': author_login, 'hashed_password': author_hashed_password}
    return _author


def secret_key():
    return os.getenv("SECRET_KEY")
