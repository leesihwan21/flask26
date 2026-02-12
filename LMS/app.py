# pip install flask -> flask 설치하는 것. 서버처럼 돌리는 것. ip에 포트번호 생성. while문 대체
# flask(플라스크)란
# 파이썬으로 만든 db 연동 콘솔 프로그램을 웹으로 연결하는 프레임워크다.
import os.path

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pymysql import connect

# 터미널에서 pip install flask 다운로드. 후 진행.

#          플라스크 클래스,    프론트연결,     요청,응답, 주소전달,  주소로보냄, 상태저장
from LMS.common import Session
from LMS.domain import Board, Score
from LMS.service import PostService

# ######################################################################################################################
# 풀스텍을 할 때 순서
# 1. UI - > 프론트를 먼저 구상을 해야함. 레이아웃? (프론트 화면)
# 2. LMS DB (MySQL) -> database
# 3. 순서를 ai 한테 물어볼 것.
# ######################################################################################################################



# 프레임워크 : 미리 만들어 놓은 틀 안에서 작업. -> 미리 만들어 놓은 것은 폴더가 정해져 있는 것.
# app.py 는 플라스크로 서버를 동작하기 위한 파일명(기본 파일)

# static, templates 폴더 필수 (프론트용 파일 모이는 곳)
# static : 정적 파일을 모아놓는 것. (html, css, js,,,)
# templates : 동적 파일을 모아놓는 것. (crud 화면, 레이아웃, 인덱스 등....)

app = Flask(__name__)
app.secret_key = '1234'
# RuntimeError ; The session is unavailable because no secret key was set.
# set the secret_key on the application to something unique and secret.

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
# 세션을 사용하기 위해 보안키 설정 (아무 문자열이나 입력)
# RuntimeError: The session is unavailable because no secret key was set.
# Set the secret_key on the application to something unique and secret.

@app.route('/login', methods=['GET','POST']) # http://localhost:5000/login
    # methods는 웹에 동작을 관여한다.
    # GET : URL 주소로 데이터를 처리(보안상 좋지 않음, 빠름)
    # POST : BODY영역에서 데이터를 철리(보안상 좋음, 대용량에서 많이 사용함)
    # 대부분 처음에 화면(HTML렌더)을 요청할 때는 GET 방식으로 처리
    # 화면에 있는 내용을 백엔드로 전달할 때는 POST 방식으로 처리
def login():
    if request.method == 'GET': # 처음접속하면 GET방식으로 화면 출력용
        return render_template('login.html')
        # get방식으로 요청하면 login.html 화면이 나옴

    # login.html에서 action="/login" method="POST"처리용 코드
    # login.html에서 넘어온 폼 데이터는 uid / upw
    uid = request.form.get('uid') # 요청한  폼내용을 가져옴
    upw = request.form.get('upw') # request  form  get
    # print("/login에서 넘어온 폼 데이터 출력 테스트 ")
    # print(uid, upw)
    # print("===================================")

    conn = Session.get_connection() # 교사용 db에 접속용 객체
    try: # 예외발생 가능성 있음
        with conn.cursor() as cursor: # db에 커서객체 사용
            # 1회원 정보 조회
            sql = "SELECT id, name, uid, role  \
            FROM members WHERE uid = %s AND password = %s"
            #                  uid가 동일 &  pwd가 동일
            #    id, name, uid, role 가져온다.
            cursor.execute(sql, (uid, upw)) # 쿼리문 실행
            user = cursor.fetchone() # 쿼리 결과 1개를 가져와 user 변수에 넣음

            if user:
                # 찾은 계정이 있으면 브라우져의 세션영역에 보관한다.
                session['user_id'] = user['id'] # 계정일련번호(회원번호)
                session['user_name'] = user['name'] # 계정이름
                session['user_uid'] = user['uid']  # 계정로그인명
                session['user_role'] = user['role']  # 계정권한
                # 세션에 저장 완료
                # 브라우저에서 f12번 누르고 애플리케이션 탭에서 쿠키 항복에 가면 session객체가 보임
                # 이것을 삭제하면 로그아웃 처리 됨
                return redirect(url_for('index'))
                # 처리후 이동하는 경로 http://localhost:/index로 감(get 메서드 방식)
            else :
                # 찾은 계정이 없다.
                return "<script>alert('아이디나 비번이 틀렸습니다.');history.back();</script>"
            #                  경고창발생                          뒤로가기
    finally:
        conn.close() # db 연결 종료


@app.route('/logout') # 기본동작이 get방식이라 , methods=['GET'] 생략가능
def logout():
    session.clear()  # 세션 비우기
    return redirect(url_for('login'))# http://localhost:5000/login (get방식)

@app.route('/join', methods=['GET','POST']) # 회원가입용 함수
def join(): # http://localhost:5000/ get메서드(화면출력) post(화면폼처리용)
    if request.method == 'GET':
        return render_template('join.html') # 로그인화면용 프론트로 보냄

    # POST 메서드 인 경우 (폼으로 데이터가 넘어올때 처리)

    uid = request.form.get('uid')
    password = request.form.get('password')
    name = request.form.get('name') # 폼에서 넘어온 값을 변수에 넣음

    conn = Session.get_connection() # db에 연결
    try: # 예외발생 가능성이 있는 코드
        with conn.cursor() as cursor:
            # 아이디 중복 확인
            cursor.execute("SELECT id FROM members WHERE uid = %s", (uid,))
            if cursor.fetchone():
                return "<script>alert('이미 존재하는 아이디입니다.'); history.back();</script>"

            # 회원 정보 저장 (role, active는 기본값이 들어감)
            sql = "INSERT INTO members (uid, password, name) VALUES (%s, %s, %s)"
            cursor.execute(sql, (uid, password, name))
            conn.commit()

            return "<script>alert('회원가입이 완료되었습니다!'); location.href='/login';</script>"
    except Exception as e: # 예외발생시 실행문
        print(f"회원가입 에러: {e}")
        return "가입 중 오류가 발생했습니다. /n join()메서드를 확인하세요!!!"

    finally:   # 항상 실행문
        conn.close()


@app.route('/member/edit', methods=['GET', 'POST'])
def member_edit():
    if 'user_id' not in session: # 셔센에 user_id가 없으면
        return redirect(url_for('login'))  # 로그인 경로로 보냄

    # 있으면 db연결 시작!
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                # 기존 정보 불러오기
                cursor.execute("SELECT * FROM members WHERE id = %s", (session['user_id'],))
                user_info = cursor.fetchone()
                return render_template('member_edit.html', user=user_info)
                #                     가장 중요한 포인트    get요청시 페이지     객체 전달용 코드

            # POST 요청: 정보 업데이트
            new_name = request.form.get('name')
            new_pw = request.form.get('password')

            if new_pw:  # 비밀번호 입력 시에만 변경
                sql = "UPDATE members SET name = %s, password = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_pw, session['user_id']))
            else:  # 이름만 변경
                sql = "UPDATE members SET name = %s WHERE id = %s"
                cursor.execute(sql, (new_name, session['user_id']))

            conn.commit()
            session['user_name'] = new_name  # 세션 이름 정보도 갱신
            return "<script>alert('정보가 수정되었습니다.'); location.href='/mypage';</script>"

    except Exception as e:# 예외발생시 실행문
        print(f"회원수정 에러: {e}")
        return "수정 중 오류가 발생했습니다. /n member_edit()메서드를 확인하세요!!!"

    finally:  # 항상 실행문
        conn.close()

@app.route('/mypage') # http://localhost:5000/mypage get요청시 처리됨
def mypage():
    # @app.route('/mypage) -> 뒤에 / 마지막 슬래시를 붙여주냐 안 붙여주냐에 따라서도 Flask는 이를 서로 다른 방식으로 처리함.
    # 슬래시가 있는 경로 (/board/) 는 마치 ** 디렉토리(폴더)** 처럼 취급함.
    # 슬래시가 없는 경로 (/mypage) 는 마치 하나의 파일처럼 취급함.
    # Flask의 설계 의도는 "URL 의 유일성"을 보장하기 위함이다.
    if 'user_id' not in session: # 로그인상태인지 확인
        return redirect(url_for('login')) # 로그인아니면 http://localhost:5000/login으로 보냄

    conn = Session.get_connection() # db연결
    try:
        with conn.cursor() as cursor:
            # 1. 내 상세 정보 조회
            cursor.execute("SELECT * FROM members WHERE id = %s", (session['user_id'],))
            # 로그인한 정보를 가지고 db에서 찾아옴
            user_info = cursor.fetchone() # 찾아온값1개를 user_info에 담음 (dict)

            # 2. 내가 쓴 게시글 개수 조회 (작성하신 boards 테이블 활용)
            cursor.execute("SELECT COUNT(*) as board_count FROM boards WHERE member_id = %s", (session['user_id'],))
            #                                                   boards 테이블에 조건 member_id 값을 가지고 찾아옴
            #                     개수를 세어 fetchone()넣음 -> board_count 이름으로 개수를 가지고 있음
            board_count = cursor.fetchone()['board_count']

            return render_template('mypage.html', user=user_info, board_count=board_count)
            # 결과를 리턴한다.                         mypage.html 에게 user객체와 board_count객체를 담아 보냄
            # 프론트에서 사용하려면 {{ user.???? }}  {{ board_count }}

    finally:
        conn.close()
#################################### 회원 CRUD END #####################################################################

#################################### 게시판 CRUD ########################################################################

@app.route('/board/write', methods=['GET', 'POST']) # http://localhost:5000/board/write
def board_write():
    # 1. 사용자가 '글쓰기' 버튼을 눌러서 들어왔을 때 (화면 보여주기)
    if request.method == 'GET':
        # 로그인 체크 (로그인 안 했으면 글 못 쓰게)
        if 'user_id' not in session:
            return '<script>alert("로그인 후 이용 가능합니다."); location.href="/login";</script>'
        return render_template('board_write.html')

        # 2. 사용자가 '등록하기' 버튼을 눌러서 데이터를 보냈을 때 (DB 저장)
    elif request.method == 'POST': # <form action="/board/write" method="POST">
        title = request.form.get('title')
        content = request.form.get('content')
        # 세션에 저장된 로그인 유저의 id (member_id)
        member_id = session.get('user_id')

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO boards (member_id, title, content) VALUES (%s, %s, %s)"
                cursor.execute(sql, (member_id, title, content))
                conn.commit()
            return redirect(url_for('board_list'))  # 저장 후 목록으로 이동
        except Exception as e:
            print(f"글쓰기 에러: {e}")
            return "저장 중 에러가 발생했습니다."
        finally:
            conn.close()


# 1. 게시판 목록 조회
@app.route('/board/') # http://localhost:5000/board
def board_list():
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # 작성자 이름을 함께 가져오기 위해 JOIN 사용
            sql = """
                SELECT b.*, m.name as writer_name 
                FROM boards b 
                JOIN members m ON b.member_id = m.id 
                ORDER BY b.id DESC 
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            boards = [Board.from_db(row) for row in rows] # from LMS.domain import Board
            return render_template('board_list.html', boards=boards)
    finally:
        conn.close()

# 2. 게시글 자세히 보기
@app.route('/board/view/<int:board_id>') # http://localhost:5000/board/view/99(게시물번호)
def board_view(board_id):
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # JOIN을 통해 작성자 정보(name, uid)를 함께 조회
            sql = """
                SELECT b.*, m.name as writer_name, m.uid as writer_uid
                FROM boards b
                JOIN members m ON b.member_id = m.id
                WHERE b.id = %s
            """
            cursor.execute(sql, (board_id,))
            row = cursor.fetchone()
            print(row) # db에서 나온 dict타입 콘솔에 출력 테스트용
            if not row:
                return "<script>alert('존재하지 않는 게시글입니다.'); history.back();</script>"

            # Board 객체로 변환 (앞서 작성한 Board.py의 from_db 활용)
            board = Board.from_db(row)

            return render_template('board_view.html', board=board)
    finally:
        conn.close()

@app.route('/board/edit/<int:board_id>', methods=['GET', 'POST'])
def board_edit(board_id):
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 화면 보여주기 (기존 데이터 로드)
            if request.method == 'GET':
                sql = "SELECT * FROM boards WHERE id = %s"
                cursor.execute(sql, (board_id,))
                row = cursor.fetchone()

                if not row:
                    return "<script>alert('존재하지 않는 게시글입니다.'); history.back();</script>"

                # 본인 확인 로직 (필요시 추가)
                if row['member_id'] != session.get('user_id'):
                    return "<script>alert('수정 권한이 없습니다.'); history.back();</script>"
                print(row) # 콘솔에 출력 테스트용
                board = Board.from_db(row)
                return render_template('board_edit.html', board=board)

            # 2. 실제 DB 업데이트 처리
            elif request.method == 'POST':
                title = request.form.get('title')
                content = request.form.get('content')

                sql = "UPDATE boards SET title=%s, content=%s WHERE id=%s"
                cursor.execute(sql, (title, content, board_id))
                conn.commit()

                return redirect(url_for('board_view', board_id=board_id))
    finally:
        conn.close()

@app.route('/board/delete/<int:board_id>')
def board_delete(board_id):

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM boards WHERE id = %s"  # 저장된 테이블명 boards 사용
            cursor.execute(sql, (board_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"게시글 {board_id}번 삭제 성공")
            else:
                return "<script>alert('삭제할 게시글이 없거나 권한이 없습니다.'); history.back();</script>"

        return redirect(url_for('board_list'))
    except Exception as e:
        print(f"삭제 에러: {e}")
        return "삭제 중 오류가 발생했습니다."
    finally:
        conn.close()


#################################### 게시판 CRUD END ####################################################################

#################################### 성적 CRUD 시작  #####################################################################
# 주의사항 : ROLE에 ADMIN과 MANAGER만 CUD (CREATE, UPDATE, DELETE) 만 제공한다.
# 일반 사용자는 ROLE이 USER이고 자신의 성적만 볼 수 있다.
@app.route('/score/add') # http://localhost:5000/score/add?uid=test1&name=test1(uid key, test1 value)
def score_add():
    if session.get('user_role') not in  ('admin','manager'):
        return "<script>alert('권한이 없습니다.'); history.back();</script>"


    # request.args는 URL을 통해서 넘어오는 값. 주소뒤에 ? KEY, VALUE&KEY VALUE... 이런식으로 계속 쓸 수 있다.(주소창에)
    target_uid = request.args.get('uid') # student 01 번을 가져옴 -> test1
    target_name = request.args.get('name') # '홍길동'을 가져옴.

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 대상 학생 id 찾기
            cursor.execute("select id from members where uid = %s", (target_uid,))
            student = cursor.fetchone()

            # 2. 기존 성적이 있는지 조회
            existing_score = None # 성적이 있을 수도 있고 없을 수도 있고. 없으면 INSERT 있으면 수정 UPDATE. INDATE? -> INSERT + UPDATE
            if student: # 학생번호가 있으면 밑에 함수문 실행
                cursor.execute("select * from scores where member_id = %s", (student['id'],)) # student id 는 학생의 번호
                row = cursor.fetchone()
                print(row) # 출력 테스트용 코드로 dict 타입으로 출력됨.
                if row:
                    # 기존에 만든 Score.from_db 활용
                    existing_score = Score.from_db(row)
                    # 위쪽에 객체 로드 처리 : from LMS.domain import Board, Score


            return render_template('score_form.html',
                                   target_uid=target_uid,
                                   target_name=target_name,
                                   score=existing_score) # score 객체 전달 # existing_score 써야 나옴.
                                   # 신규 등록창을 보고 싶게 하려면 MySQL 에 저장된 Score 객체를 None 값으로 처리하면 됨.
                                  # 그러면, 신규등록창이 나옴. 수정창을 보고싶다 하면 ? existing_score.
    finally:
        conn.close()


@app.route('/score/save', methods=['POST']) # POST만을 쓰는 이유는, DB, MySQL에 텍스트를 저장하는 것 뿐 아니라,
# 서버에 무언가 흔적을 남기거나 바꾸는 "모든 행위" 에 대해서 POST를 사용한다.
# 데이터의 생성/수정/삭제 (CUD) -> DB에 새로운 내용을 집어넣거나, 기존 내용을 고치거나, 지울떄 사용하고
# 보안이 필요한 정보 -> 예를 들면 로그인 할 떄 아이디랑 비밀번호를 GET으로 보내면 주소창에  ??? ID = ADMIN&PW=1234 ,, 이런식으로..???
# 그래서 POST는 데이터 주소가 아닌 HTML BODY 영역 안에 숨겨서 보낸다.
# 용량이 큰 데이터를 다룰 때, 주소창(GET)은 글자 수 제한이 있다. 하지만, POST는 이미지 파일, 긴 본문의 글, 영상 등 대용량 데이터를 보낼 수 있다.
# 한마디로, GET은 웹 브라우저 창을 띄울때, POST는 HTML, CSS, JS 를 사용할 떄 사용한다.
def score_save():
    if session.get('user_role') not in ('admin','manager'):
        return "권한 오류", 403
    # 웹 페이지에 오류 페이지로 교체

    # 폼 데이터 수집
    target_uid = request.form.get('target_uid')
    print(f"---[디버깅] HTML에서 넘어온 UID: {target_uid}-----")
    # member_id = request.form.get('member_id')
    kor = int(request.form.get('korean', 0))
    eng = int(request.form.get('english', 0))
    math = int(request.form.get('math', 0))
    issue_date = request.form.get('issue_date')

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 대상 학생의 id(pk) 가져오기 -> 학생의 번호를 가져온다.
            sql_find_member = "select id from members where uid = %s"
            cursor.execute(sql_find_member, (target_uid,))
            # cursor.execute("select * from scores where member_id = %s", (target_uid,))
            member = cursor.fetchone()
            # member = cursor.fetchone()
            print(member) # 학번 출력

            if not member: # 학번이 없다면 없으면?
                print(f"--- [오류!!] members 테이블에 {target_uid} 학생이 존재하지 않습니다. !!!-----")
                return "<script>alert('존재하지 않는 학생입니다.'); history.back();</script>" # 존재하지 않으면 history back 뒤로가기

            # 2. MySQL 에서 실제 저장된 값을 찾아낸 예를들면 숫자 PK(PRIMARY KEY  : 5) 변수에 담는다.
            #real_db_id = member['id']
            #cursor.execute("select id from scores where member_id = %s", (real_db_id,))
            #is_exist = cursor.fetchone()

            #if is_exist:
                # update 로직
                sql = "update scores set korean=%s, english=%s, math=%s, total=%s, average=%s, where member_id = %s"

            #else:
                # insert 로직
                sql = "insert into scores values (%s, %s, %s, %s, %s, %s)"
            #conn.commit()
            # return f"<script>alert('{target_uid} 저장 완료.'); history.back();</script>"
            # print(f"---[성공] {target_uid} 학생의 진짜 번호는 {real_db_id}번 입니다.-----")

            # 3. 진짜 번호를 변수에 담고 출력
            # real_id = member['id']
            # print(f"-----[디버깅] 찾은 실제 번호(PK) : {real_id}---")

            #============ DB (MySQL) 와 app.py 랑 연동해서 웹 브라우저로 화면에 내보내고 싶을 떄
            #============ 웹 브라우저(홈페이지) 에서 예를들면 mysql에서는 members 라고 되어있는데
            #============ 파이썬에서는 target_uid 로 해놔서 "존재하지 않는 학생. 존재하지 않습니다." 라고 나오게 되면
            # scores 테이블의 member_id 컬럼은 members 테이블의 id(숫자 PK)를 참조하는 숫자 타입
            # MySQL에서 WHERE member_id = 'test1'이라고 검색하면, 숫자가 들어가야 할 자리에 문자가 들어왔으므로 검색 결과가 0건(None)이 됩니다.
            # 결과가 None 이니 파이썬에 코드는 if not student 조건문에 걸려서 , "존재하지 않는 학생" "존재하지 않습니다"? 라고 나오는 것이다.

            # 2. score 객체 생성 (계산 프로퍼티 활용)
            temp_score = Score(member_id=member['id'], kor=kor, eng=eng, math=math)
            #             __init__ 를 활용하여 객체 생성

            # 3. 기존 데이터가 있는지 확인
            cursor.execute("select id from scores where member_id = %s", (member['id'],))
            is_exist = cursor.fetchone() # 성적이 있으면 id가 나오고, 없으면  None 처리.

            if is_exist:
                # UPDATE 실행
                sql = """
                     UPDATE scores SET korean=%s, english=%s, math=%s,
                                        total=%s, average=%s, grade=%s
                     WHERE member_id = %s
                """
                cursor.execute(sql, (temp_score.kor, temp_score.eng,
                                     temp_score.math, temp_score.total,
                                     temp_score.avg, temp_score.grade,
                                     member['id'])) # student 는 WHERE 조건. MySQL.

            else:
                # INSERT 실행
                sql = """
                    INSERT INTO scores (member_id, korean, english, math, total, average, grade)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (member['id'], temp_score.kor, temp_score.eng, temp_score.math,
                                     temp_score.total, temp_score.avg, temp_score.grade))

                conn.commit()
                return f"<script>alert('{target_uid} 학생 성적 저장 완료.');location.href='/score/list';</script>"

    #except Exception as e:
        #conn.rollback()  # 에러 발생 시 되돌리기
        #print(f"Error: {e}")  # 에러 로그 확인용
        #return f"저장 중 오류 발생: {e}"

    finally:
        conn.close()

@app.route('/score/list') # http://localhost:5000/score/list -> 기본적으로 get 방식. methods 삽입 안하면
def score_list():
    # 1. 권한 체크
    if session.get('user_role') not in ('admin','manager'):
        return "<script>alert('권한이 없습니다.)'); history.back();</script>"

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # 2. join을 사용하여 학생 이름 (name) 과 성적 데이터를 함께 조회
            # 성적이 없는 학생은 제외하고, 성적이 있는 학생들만 총점 순으로 정렬
            sql = """
                SELECT m.name, m.uid, s.*, DATE_FORMAT(s.created_at, '%%Y-%%m-%%d') as date_str 
                FROM scores s
                join members m on s.member_id = m.id
                order by s.total desc
            """
            # desc 데스크는 내림차순
            cursor.execute(sql)
            datas = cursor.fetchall()
            print(f"MySQL 결과 테스트 : {datas}")  # 출력 테스트용

            # 3. db에서 가져온 딕셔너리 리스트를 score 객체 리스트로 변환
            score_obj = []
            for data in datas:
                # score 클래스에 정의하신 from_db 활용
                s = Score.from_db(data) # 직렬화(dict 타입을 -> 객체로 만듬)
                # 객체에 없는 이름 (name) 정보는 수동으로 살짝 넣어주기 (join에서 만든 값 사용)
                s.name = data['name']
                s.uid = data['uid']
                score_obj.append(s) # 객체를 리스트 뒤에 추가함. .append 주소를 연결하는 것이 객체. 문자열이니까 객체가 없어서 객체화를 사용함.
                # 객체를 리스트화 시켜야 하니까 직렬화로 객체화 시킴.

            return render_template('score_list.html', scores=score_obj)
            # render_template       프론트 홤녀 ui에                      성적이 담긴 리스트 객체를 전달함.
    finally:
        conn.close()


@app.route('/score/members')
def score_members():
    if session.get('user_role') not in ('admin','manager'):
        return "<script>alert('권한이 없습니다.'); history.back();</script>"

    #1. 검색어 가져오기
    # search = request.args.get('search', '')

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # LEFT JOIN 을 통해서 성적이 있으면 s.id가 숫자로, 없으면 NULL 로 나옴.
            sql = """
                SELECT m.id, m.uid, s.id AS score_id
                FROM members m
                LEFT JOIN scores s ON m.id = s.member_id
                WHERE m.role = 'user'
                ORDER BY m.name DESC
            """

            # 3. 검색어가 있으면 WHERE 절 추가
            # if search:
                # sql += "WHERE m.uid LIKE %s OR m.name LIKE %s"
                # sql += "ORDER BY m.name ASC"
                # cursor.execute(sql, (f"%{search}%", f"%{search}%"))
            # else:
                # sql += "ORDER BY m.name ASC" # 전체 정렬
                # cursor.execute(sql)

            # members = cursor.fetchall()

            # 4. 검색어(search_keyword)를 꼭 넘겨주어야 화면에 출력됨.
            # return render_template('현재 수정중인 파일이름.html',
                               # members=members,
                               # search_keyword=search)

            cursor.execute(sql)
            members = cursor.fetchall()
            return render_template('score_member_list.html', members=members)

    finally:
        conn.close()


@app.route('/score/my') # http://localhost:5000/score/my - > get
def score_my():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # 내 id 로만 조회
            sql = "SELECT * FROM scores WHERE member_id = %s"
            cursor.execute(sql, (session['user_id'],))
            row = cursor.fetchone()
            print(row) # 출력 테스트용 dict 타입으로 출력됨.
            # Score 객체로 변환 (from _ db 활용)
            score = Score.from_db(row) if row else None

            return render_template('score_my.html', score=score)

    finally:
        conn.close()

#################################### 성적 CRUD 종료  ####################################################################

#################################### 파일(자료)게시판 CRUD 시작 ###########################################################

# 파일처리용 게시판은 특징
# 1. 파일 업로드 / 다운로드가 가능해야함.
# 2. 단일 파일 / 다중 파일 업로드가 가능해야함. -> 다중 파일에 대해서 공부할 것.
# 3. 서비스 패키지를 활용 -> app.py 에 한번에 다 몰려있어서 하나씩 서비스 객체로 뺀다.
# 4. /UPLOAD라는 폴더를 사용하겠다. / 용량제한 16MB
# 5. 파일명 중복방지용 코드 활용하겠다. -> 동일파일명이 올라갔을 떄 어떻게 처리할 건지?
# 6. DB에서 부모객체가 삭제되면 자식객체도 삭제 되게 CASCADE 처리함.

UPLOAD_FOLDER = 'uploads/'
# 폴더가 없으면 자동 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER) # makedirs -> 폴더생성 make directory
    # 폴더 생성용 코드는 os.makedirs(경로)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 최대 업로드 용량 제한 (예: 16mb)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# bit -> 0, 1
# byte -> 8 bit 를 1 byte 라고 부름. -> 2진법 칸 8개
# 8 byte 는 0~255 개를 가지고 있음. 256개.
# 1KB -> 1024Byte
# 1MB -> 1024KByte
# 1GB -> 1024MByte
# 1TB -> 1024GByte
# 1PB -> 1024TByte
# 1XB -> 1024PByte

@app.route('/filesboard/write', methods=['GET','POST'])
def filesboard_write():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # 핵심 : getlist를 사용해야 리스트 형태로 가져옴.
        files = request.files.getlist('files')

        if PostService.save_post(session['user_id'], title, content, files):
            return "<script>alert('게시글이 등록되었습니다.'); location.href='/filesboard';</script>"
        else:
            return "<script>alert('게시글 등록이 안 되었습니다.');history.back();</script>"

    return render_template('filesboard_write.html')


# 파일게시물 자세히보기
@staticmethod
def get_post_detail(post_id):
    """게시글 상세 정보와 첨부파일 정보를 함께 조회"""
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 조회수 증가
            cursor.execute("UPDATE posts SET view_count = view_count + 1 WHERE id = %s", (post_id,))

            # 2. 게시글 정보 조회 (작성자 이름 포함)
            sql_post = """
                        SELECT p.*, m.name as writer_name 
                        FROM posts p
                        JOIN members m ON p.member_id = m.id
                        WHERE p.id = %s
                """
            cursor.execute(sql_post, (post_id,))
            post = cursor.fetchone()

            # 3. 첨부파일 정보 조회
            cursor.execute("SELECT * FROM attachments WHERE post_id = %s", (post_id,))
            files = cursor.fetchall()

            conn.commit()
            return post, files
            # post는 posts에 있는 자료, files는 첨부 파일에 대한 자료. 이 2개가 넘어감.
    finally:
        conn.close()


# 파일 게시물 목록
@staticmethod
def get_posts():
    """작성자 이름과 첨부파일 개수를 함께 조회"""
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            # 서브쿼리를 사용하여 해당 게시글에 연결된 첨부파일 개수(file_count)를 가져옵니다.
            sql = """
                       SELECT p.*, m.name as writer_name,
                              (SELECT COUNT(*) FROM attachments WHERE post_id = p.id) as file_count
                       FROM posts p
                       JOIN members m ON p.member_id = m.id
                       ORDER BY p.created_at DESC
                   """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()



# 파일 게시판 목록
@app.route('/filesboard')
def filesboard_list():
    posts = PostService.get_posts()
    return render_template('filesboard_list.html', posts=posts)


# 파일 게시판 상세 보기
@app.route('/filesboard/view/<int:post_id>')
def filesboard_view(post_id):
    post, files = PostService.get_post_detail(post_id)
    if not post:
        return "<script>alert('해당 게시글이 없습니다.'); location.href='/filesboard';</script>"
    return render_template('filesboard_view.html', post=post, files=files)


# send_from_directory 사용하여 자료 다운로드 가능
@app.route('/download/<path:filename>')
def download_file(filename):
    # 파일이 저장된 폴더(uploads)에서 파일을 찾아 전송합니다.
    # 프론트 <a href="{{ url_for('download_file', filename=file.save_name) }}" ...> 이부분 처리용
    # filename은 서버에 저장된 save_name입니다.
    # 브라우저가 다운로드할 때 보여줄 원본 이름을 쿼리 스트링으로 받거나 DB에서 가져와야 합니다.
    origin_name = request.args.get('origin_name')
    return send_from_directory('uploads/', filename, as_attachment=True, download_name=origin_name)
    # from flask import send_from_directory 필수

    #   return send_from_directory('uploads/', filename)는 브라우져에서 바로 열어버림
    #   as_attachment=True 로 하면 파일 다운로드 창을 띄움
    #   저장할 파일명은 download_name=origin_name 로 지정




############################################# 파일 upload 게시판 The end. ################################################


@app.route('/') # url 생성용 코드 http://localhost:5000/ or http://192.168.0.???:5000
def index():
    return render_template('main.html')
    # render_template 웹브라우저로 보낼 파일명
    # templates 라는 폴더에서 main.html을 찾아 보냄

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
    # port 번호 5000 은 강사님 번호이고 5001 번부터 연습하면 됨.
    # host='0.0.0.0' 누가요청하던 응답해라(모두 들어올 수 있게 설정함)
    # port=5000 플라스크에서 사용하는 포트번호
    # debug=True 콘솔에서 디버그를 보겠다.