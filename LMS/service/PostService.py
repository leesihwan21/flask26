import os
import uuid

from LMS.common import Session


class PostService:

    # 파일게시물 저장
    @staticmethod
    def save_post(member_id, title, content, files=None, upload_folder='uploads/'):
        """게시글과 첨부파일을 동시에 저장 (트랜잭션 처리)"""
        conn = Session.get_connection()  # from LMS.common import Session
        try:
            with conn.cursor() as cursor:
                # 1. 게시글(posts) 먼저 저장
                sql_post = "INSERT INTO posts (member_id, title, content) VALUES (%s, %s, %s)"
                cursor.execute(sql_post, (member_id, title, content))

                # 방금 INSERT된 게시글의 ID(PK) 가져오기
                post_id = cursor.lastrowid
                # 파일첨부테이블에 들어갈 내용

                # 3. 다중 파일 처리
                if files:
                    for file in files:
                        if file and file.filename != '':
                            origin_name = file.filename
                            ext = origin_name.rsplit('.', 1)[1].lower()
                            save_name = f"{uuid.uuid4().hex}.{ext}"  # 상단에 import uuid
                            file_path = os.path.join(upload_folder, save_name)  # 상단에 import os

                            file.save(file_path)  # 서버에 저장 uploads/

                            # attachments 테이블에 각각 저장
                            sql_file = """INSERT INTO attachments (post_id, origin_name, save_name, file_path)
                                          VALUES (%s, %s, %s, %s)"""
                            cursor.execute(sql_file, (post_id, origin_name, save_name, file_path))

                conn.commit()
                return True

        except Exception as e:
            print(f"Error saving post: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()  # save_post(member_id, title, content, files, upload_folder) -> True / False

    # 파일게시물 목록
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
                return post, files # post는 posts에 있는 자료 / files는 첨부파일에 대한 자료
        finally:
            conn.close()

    @staticmethod
    def delete_post(post_id, upload_folder='uploads/'):
        """게시글 및 관련 실제 파일 삭제"""
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 삭제 전 첨부파일 정보 조회 (파일 삭제를 위해)
                cursor.execute("SELECT save_name FROM attachments WHERE post_id = %s", (post_id,))
                files = cursor.fetchall()

                # 2. 서버에서 실제 파일 삭제
                for f in files:
                    file_path = os.path.join(upload_folder, f['save_name'])
                    if os.path.exists(file_path):
                        # 파일이 실제로 존재하는지 확인.
                        # 만약 파일이 이미 지워졌거나 이름이 바뀌어서 없는데 삭제(remove)를 시도하면 프로그램이 에러를 내며 멈춰버리기 때문
                        # os.remove(file_path):확인이 끝난 파일을 서버 하드디스크에서 영구적으로 삭제
                        os.remove(file_path) # 실제 하드에서 삭제 진행

                # 3. 게시글 삭제 (DB 외래키 ON DELETE CASCADE 설정 덕분에 attachments도 자동 삭제됨)
                # 삭제시 cascade 옵션을 하지 않으면 자식 테이블 데이터를 선 삭제후 부모 테이블 데이터를 삭제
                sql = "DELETE FROM posts WHERE id = %s"
                cursor.execute(sql, (post_id,))

                conn.commit()
                return True
        except Exception as e:
            print(f"Delete Error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod  # 다중파일 수정 처리(기존파일 지우고 업데이트)
    def update_post(post_id, title, content, files=None, upload_folder='uploads/'):
        """게시글 수정 및 다중 파일 교체"""
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 기본 정보 수정
                cursor.execute("UPDATE posts SET title=%s, content=%s WHERE id=%s", (title, content, post_id))

                # 2. 새 파일들이 들어왔을 경우만 기존 파일 삭제 및 교체
                # (아무 파일도 선택 안 하면 기존 파일 유지)
                if files and any(f.filename != '' for f in files):
                    # for f in files : 업르도된 파일들을 하나씩 꺼내서 f 라고 부름.
                    # f.filename != '': 꺼낸 파일의 이름이 빈 값인지 확인
                    # any(...) : 리스트 중에서 참 (True) 인게 하나라도 있으면 전체를 True로 판단함.
                    # A. 기존 물리적 파일 삭제를 위해 save_name 조회
                    cursor.execute("SELECT save_name FROM attachments WHERE post_id = %s", (post_id,))
                    old_files = cursor.fetchall()
                    for old in old_files:
                        old_path = os.path.join(upload_folder, old['save_name'])
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    # B. DB에서 기존 첨부파일 기록 삭제
                    cursor.execute("DELETE FROM attachments WHERE post_id = %s", (post_id,))

                    # C. 새로운 파일들 저장
                    for file in files:
                        if file and file.filename != '':
                            # 사용자가 진짜로 파일을 선택해서 올렸어? 확인하는 가장 필수적 안정장치 코드
                            # 파일의 이름이 빈 문자열 '' 이 아닌지 확인
                            # 사용자가 파일 선택창을 띄우기만 하고 아무 파일도 고르지 않았는데 확인을 누르면
                            # 객체는 생성되지만 파일 이름은 빈 값''으로 서버에 전달된다.
                            # 이 if 조건문이 없으면 빈 파일을 저장하려다 에러가 날 수 있다.
                            origin_name = file.filename
                            ext = origin_name.rsplit('.', 1)[1].lower() # right 오른쪽으로부터 자른다. split. '.' => . 점을
                            # 기준으로 자르라는 기준 (구분자)
                            # 1 이란 숫자는 딱 한 번만 자르라는 뜻.
                            # .lower 라는 건 대소문자 구분 짓기 위해서. 확장자가 대문ㅁ자일수도 있고 소문자일수도 있어서
                            # 바꿔서 통일해줌.
                            save_name = f"{uuid.uuid4().hex}.{ext}"
                            # uuid.uuid4() -> 범용 고유 식별자를 생성함.
                            # 중복될 확률이 거의 제로에 가까운 무작위 ID를 만들어냄.
                            # .hex 는 생성된 UUID를 하이픈(-) 없이 32자리의 16진수 문자열로 변환해주는 기능.
                            # f"{...}.{ext} 는 f-string 기법. 앞에서 만든 무작위 문자열 뒤에 점.을 찍고, 아까 추출했던 확장자(ext)를 붙임.

                            file_path = os.path.join(upload_folder, save_name)
                            # 입력 : origin_name = "dog.png"
                            # 변환 : save_name = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6.png"
                            # 서버 폴더 안에는 이 복잡하고 고유한 이름으로 파일이 저장되므로, 수천 명이 동시에 파일을 올려도
                            # 중복되지 않고 저장할 수 있음.
                            file.save(file_path)

                            cursor.execute("""
                                        INSERT INTO attachments (post_id, origin_name, save_name, file_path)
                                        VALUES (%s, %s, %s, %s)
                                    """, (post_id, origin_name, save_name, file_path))

                conn.commit() # 진짜로 저장해.
                return True
        except Exception as e:
            print(f"Update Error: {e}")
            conn.rollback() # 원래대로 다시 복구
            return False
        finally:
            conn.close()