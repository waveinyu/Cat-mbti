from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/cat_images"

SECRET_KEY = 'CATMBTI'

client = MongoClient('mongodb+srv://test:sparta@cluster0.byzbnff.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.cat_mbti


@app.route('/')
def intro():
    msg = request.args.get("msg")
    return render_template('intro.html', msg=msg)


# 토큰 확인하고, index.html 에 user_info 넘겨주기
@app.route('/main')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        user_mbti = user_info["mbti"]
        if user_mbti:
            # 고양이 찾기, 시험 응시 유저 카운트
            cat = db.cats.find_one({'cat_mbti': user_mbti})
        else:
            cat = ""
        return render_template('index.html', user_info=user_info, cat=cat)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username = request.form['username']
    password = request.form['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    doc = {
        "username": username,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username,  # 프로필 이름 기본값은 아이디
        "mbti": "",  # mbti
        "hobby": "",  # 취미
        "color": "",  # 좋아하는 색
        "cat_pic": "",  # 프로필 사진 파일 이름
        "cat_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "status": "0",
        "date": "",  # 시험 응시때 업데이트 됨
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 로그인, 유저 찾기, 토큰 넘겨주기
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username = request.form['username']
    password = request.form['password']
    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username, 'password': pw_hash})

    # 서버에 아이디가 존재해서 결과를 받았다면 클라이언트로 토큰을 넘겨준다
    if result is not None:
        payload = {
            'id': username,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/test')
def test():
    msg = request.args.get("msg")
    return render_template('test.html', msg=msg)


# 테스트 결과 처리하는 API by JIHUN
@app.route('/test_result_update', methods=['POST'])
def test_result_update():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        mbti = request.form["mbti"]
        color = request.form["color"]
        date = request.form["date"]
        # 여기서 유저 정보 업데이트
        if user_info["status"] == "0":
            db.users.update_one({'username': user_info['username']}, {'$set': {'status': "1"}})
        db.users.update_one({'username': user_info['username']}, {'$set': {'mbti': mbti}})
        db.users.update_one({'username': user_info['username']}, {'$set': {'color': color}})
        db.users.update_one({'username': user_info['username']}, {'$set': {'date': date}})
        return jsonify({"result": "success", "msg": "시험을 완료했습니다."})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/result')
def result():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        user_mbti = user_info["mbti"]
        if user_mbti:
            # 고양이 찾기, 시험 응시 유저 카운트
            cat = db.cats.find_one({'cat_mbti': user_mbti})
            cat_name = cat['cat_name']
            waiting_users = db.users.count_documents({"status": "0"})
            user_count = db.users.count_documents({"status": "1"})
            print(user_count)
            print(cat_name)
            return render_template('result.html', cat=cat, cat_name=cat_name, waiting_users=waiting_users,
                                   user_count=user_count,
                                   user_info=user_info)
        else:
            return redirect(url_for("test", msg="시험 결과가 없습니다. 시험을 봐주세요."))
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

    # 유저의 MBTI 에 상응하는 고양이 불러오기


@app.route("/get_test_results", methods=['GET'])
def get_test_results():
    users = list(db.users.find({"status": "1"}).sort("date", -1).limit(20))
    cats = list(db.cats.find({}))
    # DATE(시험 재응시에도 적용됨), ObjectId 문자열로 변환
    for cat in cats:
        cat["_id"] = str(cat["_id"])
        print(cat)
    for user in users:
        user["_id"] = str(user["_id"])
        print(user)
    return jsonify({"result": "success", "msg": "시험을 가져왔습니다.", 'users': users, 'cats': cats})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
