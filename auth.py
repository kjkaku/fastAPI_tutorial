import hashlib
import db
from models import User
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import HTTPException


def auth(credentials, logout=False):
    """Basic認証チェック"""
    # Basic認証で受け取った情報#
    print("credentials2")
    print(credentials.username)
    username = credentials.username
    print("username")
    print(username)
    password = hashlib.md5(credentials.password.encode()).hexdigest()
    # データベースからユーザー名が一致するデータを取得
    user = db.session.query(User).filter(User.username == username).first()
    db.session.close()

    # 該当ユーザーがいない場合
    #if user is None or user.password != password:
    print("test5")
    if user is None or user.password != password:
        if user is None:
            print("test6")
        #if user.password != password:
        #    print("test4")
        error = 'ユーザー名かパスワードが間違ってます'
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Basic"},
            )
    print("test7")
    return username