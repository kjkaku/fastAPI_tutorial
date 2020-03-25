from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
 
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
 
import db
from models import User, Task
 
import hashlib

import asyncio

import re

from mycalendar import MyCalendar
from datetime import datetime
from datetime import timedelta 

from auth import auth
from starlette.responses import RedirectResponse

from fastapi import FastAPI, Depends, Form

pattern = re.compile(r'\w{4,20}')  # 任意の4~20の英数字を示す正規表現
pattern_pw = re.compile(r'\w{6,20}')  # 任意の6~20の英数字を示す正規表現
pattern_mail = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')  # e-mailの正規表現

app = FastAPI(
    title='FastAPIでつくるtoDoアプリケーション',
    description='FastAPIチュートリアル：FastAPI（とstarlette）でシンプルなtoDoアプリを作りましょう.',
    version='0.9 beta'
)

print("test1")
security = HTTPBasic()
print("test2")
# new テンプレート関連の設定（jinja2）
templates = Jinja2Templates(directory="templates")
jinja_env = templates.env # Jinja2.Environment : filterやglobalの設定用


def index(request: Request):
    print("test3")
    return templates.TemplateResponse('index.html',
                                      {'request': request}) # new 変更

def admin(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    # Basic認証で受け取った情報
    print("credentials4")
    print(credentials.username)
    username = auth(credentials)#.username

    # データベースからユーザ名が一致するデータを取得
    user = db.session.query(User).filter(User.username == username).first()
    #task = db.session.query(Task).filter(Task.user_id == user.id).all() if user is not None else []
    task = db.session.query(Task).filter(Task.user_id == user.id).all()
    db.session.close()


    """ [new] 今日の日付と来週の日付"""
    today = datetime.now()
    next_w = today + timedelta(days=7) # 1週間後の日付




    """
    # 該当ユーザがいない場合
    if user is None or user.password != password:
        error = 'ユーザ名かパスワードが間違っています'
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Basic"},
        )
    """
    task = db.session.query(Task).filter(Task.user_id == user.id).all()
    db.session.close()

    """[new] カレンダー関連"""
    # カレンダーをHTML形式で取得
    cal = MyCalendar(username,
                     {t.deadline.strftime('%Y%m%d'): t.done for t in task}) # 予定がある日付をキーとして渡す
                      
    cal = cal.formatyear(today.year, 4) # カレンダーをHTMLで取得

    task = [t for t in task if today <= t.deadline <= next_w]
    links = [t.deadline.strftime('/todo/'+username+'/%Y/%m/%d') for t in task] # 直近の予定のリンク
    
    if request.method is 'GET':
        return templates.TemplateResponse('register.html',
                                          {'request': request,
                                           'username': '',
                                           'error': []})
    
    # 特に問題がなければ管理者ページへ
    return templates.TemplateResponse('admin.html',
                                      {'request': request,
                                       'user': user,
                                       'task': task,
                                       'links': links,
                                       'calendar':cal})




# controllers.py
async def register(request: Request):
    if request.method == 'GET':
        return templates.TemplateResponse('register.html',
                                          {'request': request,
                                           'username': '',
                                           'error': []})
 
    if request.method == 'POST':
        # POSTデータ
        data = await request.form()
        username = data.get('username')
        password = data.get('password')
        password_tmp = data.get('password_tmp')
        mail = data.get('mail')

        # new ここから
        error = []

        tmp_user = db.session.query(User).filter(User.username == username).first()

        # 怒涛のエラー処理
        if tmp_user is not None:
            error.append('同じ名前のユーザが存在します')
        if password != password_tmp:
            error.append('入力したパスワードが一致しません')
        if pattern.match(username) is None:
            error.append('ユーザ名は4-20文字の半角英数字にしてください')
        if pattern_pw.match(password) is None:
            error.append('パスワードは6-20文字の半角英数字にしてください')
        if pattern_mail.match(mail) is None:
            error.append('正しくメールアドレスを入力してください')

        if error:
            return templates.TemplateResponse('register.html',
                                              {'request': request,
                                               'username': username,
                                               'error': error})
            
        # 問題がなければユーザ登録
        user = User(username, password, mail)
        db.session.add(user)
        db.session.commit()
        db.session.close()

        return templates.TemplateResponse('complete.html',
                                          {'request': request,
                                           'username': username})

def detail(request: Request, username, year, month, day,
           credentials: HTTPBasicCredentials = Depends(security)):
    """ URLパターンは引数で取得可能 """
    # 認証オーケー？
    username_tmp = auth(credentials)
    
    if username_tmp != username: # もし他のユーザーが訪問してきたら弾く
        return RedirectResponse('/')
    
    # ログインユーザを取得
    user = db.session.query(User).filter(User.username == username).first()
    # ログインユーザーのタスクを取得
    task = db.session.query(Task).filter(Task.user_id == user.id).all()
    db.session.close()

    # 該当の日付と一致するだけのリストにする
    theday = '{}{}{}'.format(year, month.zfill(2), day.zfill(2)) # 月日は0で埋める
    task = [t for t in task if t.deadline.strftime('%Y%m%d') == theday]
    return templates.TemplateResponse('detail.html',
                                      {'request': request,
                                       'username': username,
                                       'task': task,
                                       'year': year,
                                       'month': month,
                                       'day': day})



async def done(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    #print("t.done")

    # 認証オーケー？
    username = auth(credentials)

    # ユーザー名を取得
    user = db.session.query(User).filter(User.username == username).first()

    # ログインユーザのタスクを取得
    task = db.session.query(Task).filter(Task.user_id == user.id).all()

    # フォームで受け取ったタスクの終了判定を見て内容を変更する
    data = await request.form()
    t_dones = data.getlist('done[]') # リストとして取得

    for t in task:
        if str(t.id) in t_dones: # もしIDが一致すれば"終了した予定"となるfale
            t.done = True
    
    db.session.commit()
    db.session.close()

    return RedirectResponse('/admin')

async def add(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    # 認証
    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()

    # フォームからデータを取得
    data = await request.form()
    year = int(data['year'])
    #year = int(data.get('year'))
    month = int(data['month'])
    day = int(data['day'])
    hour = int(data['hour'])
    minute = int(data['minute'])

    deadline = datetime(year=year, month=month, day=day, 
                        hour=hour, minute=minute)
    
    # 新しくタスクを生成しコミット
    task = Task(user.id, data['content'], deadline)
    db.session.add(task)
    db.session.commit()
    db.session.close()

    return RedirectResponse('/admin')

def delete(request: Request, t_id, credentials: HTTPBasicCredentials = Depends(security)):
    # 認証
    username = auth(credentials)

    # ログインユーザー情報を取得
    user = db.session.query(User).filter(User.username == username).first()

    # 認証宅区を取得
    task = db.session.query(Task).filter(Task.id == t_id).first()

    # もしユーザIDが異なれば削除せずリダイレクト
    if task.user_id != user.id:
        return RedirectResponse('/admin')

    # 削除してコミット
    db.session.delete(task)
    db.session.commit()
    db.session.close()

    return RedirectResponse('/admin')
       
def get(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    # 認証
    print("test4")
    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()

    # タスクを取得
    task = db.session.query(Task).filter(Task.user_id ==user.id).all()

    db.session.close()

    # JSONフォーマット
    task = [{
        'id': t.id,
        'content': t.content,
        'deadline': t.deadline.strftime('%Y-%m-%d %H:%M:%S'),
        'published': t.date.strftime('%Y-%m-%d %H:%M:%S'),
        'done': t.done, 
    } for t in task]

    return task

async def insert(request: Request, 
                 content: str = Form(...), deadline: str = Form(...),
                 credentials: HTTPBasicCredentials = Depends(security)):
    """
    タスクを追加してJSONで新規タスクを返す。「deadline」は%Y-%m-%d_%H:%M:%S
    （e.g. 2019-11-03_12:30:00)の形式）
    """
    # 認証
    username = auth(credentials)

    # ユーザ情報を取得
    user = db.session.query(User).filter(User.username == username).first()

    # タスクを追加
    task = Task(user.id, content, datetime.strptime(deadline, '%Y-%m-%d_%H:%M:%S'))

    db.session.add(task)
    db.session.commit()

    # テーブルから新しく追加したタスクを取得する
    task = db.session.query(Task).all()[-1]
    db.session.close()

    # 新規タスクをJSONで返す
    return {
        'id': task.id,
        'content': task.content,
        'deadline': task.deadline.strftime('%Y-%m-%s %H:%M:%S'),
        'published': task.date.strftime('%Y-%m-%s %H:%M:%S'),
        'done': task.done,
    }

def logout(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    #error = 'ユーザー名かパスワードが間違ってます'
    #credentials.username = None
    print("credentials3")
    print(credentials.username)
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization", domain="127.0.0.1:8000")
    return response#RedirectResponse('/')
   