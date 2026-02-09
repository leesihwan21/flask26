# pip install flask -> flask 설치하는 것.
# flask(플라스크)란
# 파이썬으로 만든 db 연동 콘솔 프로그램을 웹으로 연결하는 프레임워크다.
from flask import Flask, render_template, request, redirect, url_for, session
#          플라스크 클래스,    프론트연결,     요청,응답, 주소전달,  주소생성,  상태저장
from LMS.common import Session

# 프레임워크 : 미리 만들어 놓은 틀 안에서 작업. -> 미리 만들어 놓은 것은 폴더가 정해져 있는 것.
# app.py 는 플라스크로 서버를 동작하기 위한 파일명(기본 파일)

# static, templates 폴더 필수 (프론트용 파일 모이는 곳)
# static : 정적 파일을 모아놓는 것. (html, css, js,,,)
# templates : 동적 파일을 모아놓는 것. (crud 화면, 레이아웃, 인덱스 등....)

app = Flask(__name__)
app.secret_key = '1234'
# RuntimeError ; The session is unavailable because no secret key was set.
# set the secret_key on the application to something unique and secret.

@app.route('/login', methods=['GET', 'POST']) # http://localhost:5000/login -> 이 경로로 누군가가 호출하면 화면이 먼저 보여야함
    # 여기에다가 아이디 패스워드를 쓰고 로그인 버튼을 누르면 DB까지 갔다와야함.
    # methods 는 웹의 동작에 관여한다.
    # Get은 : URL 주소로 데이터를 처리한다. 보안상 좋지 않음. 대신에 빠르다.
    # POST : Body 영역에 데이터를 처리한다. 보안상 좋음. 대용량에서 많이 사용한다. 대신에 느리다.
    # 대부분 처음에 화면을 요청할 때는 (Request) (HTML 렌더) GET 방식으로 처리하고
    # 화면에 있는 내용을 백엔드로 전달할 때는 POST를 사용함.

def login():
    if request.method == 'GET': # 처음 접속하면 GET 방식으로 화면이 출력됨.
        return render_template('login.html')
        # GET 방식으로 요청하면 login.html 화면이 나온다.

        # login.html에서 action= "/login" method="POST" 처리용 코드
        # login.html에서 넘어온 폼 데이터는 uid, upw

    uid = request.form.get('uid') # 요청한 폼 내용을 가져온다.
    upw = request.form.get('upw') # 요청한 requested form  get
    # print("/login에서 넘어온 폼 데이터 출력 테스트")
    # print(uid, upw)
    # print("===================================")
    # 웹브라우저에 로그인 페이지 화면 띄울려면 주소창에 http://localhost:5000/login -> 이렇게 입력해야됨. : 이 중요함.

    conn = Session.get_connection()
    try: # 예외발생이 있을 수 있으므로.
        with conn.cursor() as cursor: # db에 커서 객체 사용
            # 1. 회원정보 조회
            sql = 'select id, name, uid, role \
            from members where uid = %s AND password = %s'
            #                   uid 가 동일한지 pwd 가 동일한지
            #  id, name, uid, role 가져온다ㅏ.
            cursor.execute(sql, (uid, upw))
            user = cursor.fetchone() # 쿼리 결과 한개만 가져옴. user 변수에 넣음

            if user:
                # 찾은 계정이 있다. 있으면 웹 브라우저 세션영역에 보관한다.
                session['user_id'] = user['id'] # 계정 일련번호(회원번호)
                session['user_name'] = user['name'] # 계정이름(회원이름)
                session['user_uid'] = user['uid'] # 계정 로그인명
                session['user_role'] = user['role'] # 계정 권한
                # session 저장완료
                # 브라우저에서 F12 번을 누르고 Application 탭에서 쿠키 항목에 가면 세션 객체가 보인다.
                # 이것을 삭제하면 로그아웃 처리됨.
                return redirect(url_for('index'))
                # 처리 후 이동하는 경로 http://localhost:/index로 감 (get 메서드 방식)
            else:
                # 찾은 계정이 없다.
                return "<script>alert('아이디나 비밀번호가 틀렸습니다.');history.back();</script>"
                #               경고창 발생                           뒤로가기

    finally:
        conn.close() # db 연결 종료


@app.route('/logout') # 기본동작이 get 방식이라, 굳이 @app.route('get','post')를 쓸 필요가 없다.!!
def logout():
    session.clear() # 세션 비우기
    return redirect(url_for('login')) # redirect 주소 전달
    # http://localhost:5000/login (get 메서드 방식)

# app.route('/signup') 만들고 회원정보 수정 회원탈퇴 기능 추가해서 만들면 됨.
@app.route('/join', methods=['get','post']) # 회원가입용 함수
def join(): # http://localhost:5000/ get 메서드는 (화면 출력용),  post 메서드는 (화면폼처리용)
    if request.method == 'GET':
        return render_template('join.html') # 로그인 화면용 프론트로 연결

    # POST 메서드 인 경우 (폼으로 데이터가 넘어올 때 처리)

    uid = request.form.get('uid')
    password = request.form.get('password')
    name = request.form.get('name') # mysql 에 쿼리문에 적용해야함. join.html에 있는 form action 에서 넘어온 값을 변수에 입력.

    conn = Session.get_connection() # db에 연결
    try: # 예외 발생 가능성이 있는 코드
    # 쿼리문 이미 있는지
    # select 문으로 아이디 확인
    # 없으면 insert 문으로 확인
        with conn.cursor() as cursor:
            cursor.execute("select id from members where uid = %s", (uid,))
            if cursor.fetchone():
                return "<script>alert('이미 존재하는 아이디 입니다.');history.back();</script>"

            # 회원 정보 저장 (role, active 는 기본값이 들어감
            sql = "INSERT INTO members (uid, password, name) VALUES (%s, %s, %s)"
            cursor.execute(sql, (uid, password, name))
            conn.commit()

            return "<script>alert('회원가입이 완료되었습니다!'); location.href='/login';;</script>"

    except Exception as e: #  예외 발생 시 실행문
        print(f"회원가입 에러 : {e}")
        return "가입 중 오류가 발생했습니다. /n join() 메서드를 확인하세요."


    finally: # 항상 실행문
        conn.close()

# 회원정보수정
@app.route('/member/edit', methods=['get','post']) # member_edit 으로 요청이 오면 처음엔 get으로 오는데
# session 이 있는 내용이 비었으면 로그인을 해야함.
def member_edit():
    if 'user_id' not in session: # 세션에 user_id 가 없으면 login 경로로 보냄. redirect(url_for('login'))
        # 있으면 db에 연결
        return redirect(url_for('login'))

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                cursor.execute("SELECT * FROM members where id = %s", (session['user_id'],))
                user_info = cursor.fetchone() # 회원정보를 한개 가져옴. 가져와서 user_info 변수에 넣음
                return render_template('member_edit.html', user=user_info)
                #                       가장 중요한 포이트  get 요청시 페이지      객체 전달용 코드

            # post 요청 : 정보 업데이트
            new_name = request.form.get('name')
            new_pw = request.form.get('password')

            if new_pw: # 비번 입력시에만 변경
                sql = "UPDATE members SET name = %s, password = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_pw, session['user_id']))
            else: # 이름만 변경할 떄
                sql = "update members set name = %s where id = %s"
                cursor.execute(sql, (new_name, session['user_id']))

            conn.commit() # 정보 저장
            session['user_name'] = new_name # 세션 이름 정보도 갱신
            return "<script>alert('정보가 수정되었습니다.'); location.href='/my page';</script>"


    except Exception as e: # 예외 발생문
        print(f"회원수정 중 에러 : {e}")
        return "회원 수정 중 오류가 발생했습니다. /n member_edit() 메서드를 확인하세요."


    finally:
        conn.close()


@app.route('/my page') # http://localhost:5000/mypage get 요청시 처리됨
def my_page():
    if 'user_id' not in session:
        return redirect(url_for('login')) # 로그인 상태인지 확인. ex) 로그인을 하지 않았으면 로그인으로 보냄.
        #  http://localhost:5000/mypage

    conn = Session.get_connection() # db 연결. Session 대문자이면.
    try:
        with conn.cursor() as cursor:
            # 1. 내 상세 정보 조회
            cursor.execute("SELECT * FROM members where id = %s", (session['user_id'],))
            # 로그인 한 정보를 가지고 db에서 찾아온다.
            user_info = cursor.fetchone()
            # 찾아온 members 값을 user_info 에 담음 (dict) key, value

            # 2. 내가 쓴 게시글 개수 조회 (작성하신 boards 테이블 활용)
            cursor.execute("SELECT count(*) as board_count FROM boards where member_id = %s", (session['user_id'],))
            #                                                   boards 테이블에 조건 member_id 값을 가지고 찾아옴.
            #                       개수를 세어 fetchone() 에 넣음. -> board_count 라는 이름으로 개수를 가지고 있음.
            board_count = cursor.fetchone()['board_count']

            return render_template('my_page.html', user=user_info, board_count=board_count)
            # 결과를 리턴한다.                          my_page.html 에게 user객체와 board_count 객체를 담아 보낸다.
            # 프론트에서 사용하려면 { {user.???? } }, { {board_count} } -> 이런식으로 return 문에서 사용하면 된다.
    finally:
        conn.close() # finally 종료.


@app.route('/') # url 생성용 코드 http://localhost:5000/ or http://내ip(192.168.0.157.:5000
def index():
    return render_template('main.html')
    # render_template 웹브라우저로 보낼 파일명
    # templates 라는 폴더에서 main.html을 찾아 보냄.


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
    # host = '0.0.0.0', 누가 요청하던 응답해라.
    # port = 5000 플라스크에서 사용하는 포트번호
    # debug=True 콘솔에서 디버그를 보겠다.