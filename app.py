import json
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import jwt
from datetime import datetime, timedelta
import hashlib

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.sis7sux.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/main')
def main():
    return render_template('main.html')


##################################################


# 로그인
@app.route('/login/save', methods=["POST"])
def sign_in(): ##수정 로그인 페이지에서 받은 id, pw 값을 db 조회 하기
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'id': id_receive})
    if result is None:
        return jsonify({'msg':'아이디가 존재하지 않습니다.', 'result':1}) # 아이디 검증
    
    if result['pw'] == pw_hash: # 비밀번호 확인
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result':0, 'token': token})
    else:
        return jsonify({'msg':'비밀번호가 틀렸습니다.', 'result':1})
    

# 회원가입   
@app.route('/register/save', methods=["POST"])
def sign_up():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nick_receive = request.form['nick_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    
    doc = {
        'id':id_receive,
        'pw':pw_hash,
        'nick':nick_receive
    }
    # db.users.insert_one(doc)
    return jsonify({'msg':"success"})


# 아이디 중복 체크
@app.route('/register/check', methods=["POST"])
def overlap_id():
    id_receive = request.form['id_give']
    print(id_receive)
    result = db.users.find_one({'id':id_receive})
    print(result)
    # if id_receive == result:
    if result is None:
        return jsonify({'msg':"사용 가능한 아이디입니다", 'sign':"0"})
    else:
        return jsonify({'msg':"중복된 아이디입니다", 'sign':"1"})

# 닉네임 중복 체크
@app.route('/register/check_nick', methods=["POST"])
def overlap_nick():
    nick_receive = request.form['nick_give']
    print(nick_receive)
    result = db.users.find_one({'nick':nick_receive})
    print(result)
    if result is None:
        return jsonify({'msg':'사용 가능한 닉네임입니다', 'state':"success"})
    else:
        return jsonify({'msg':'중복된 닉네임입니다', 'state':"fail"})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

