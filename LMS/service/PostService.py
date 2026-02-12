import os
import sqlite3
import uuid

from LMS.common import Session

class PostService:

    # 파일게시물 저장
    @staticmethod
    def save_post(member_id, title, content, files=None, upload_folder='uploads/'):
        """게시글과 첨부파일을 동시에 저장 (트랜잭션 처리)"""
        conn = Session.get_connection() # from LMS.common import Session.
        try:
            with conn.cursor() as cursor:
                # 1. 게시글(post) 먼저 저장
                sql_post = "INSERT INTO posts (member_id, title, content) VALUES (%s, %s, %s)"
                cursor.execute(sql_post, (member_id, title, content))

                # 방금 INSERT 된 게시글의 ID(PK) 가져오기
                post_id = cursor.lastrowid
                # 파일 첨부 테이블에 들어갈 내용 -> post_id

                # 3. 다중 파일 처리용 코드
                if files:
                    for file in files:
                        if file and file.filename != '':
                            origin_name = file.filename
                            ext = origin_name.rsplit('.',1)[1].lower()
                            save_name = f"{uuid.uuid4().hex}.{ext}"
                            file_path = os.path.join(upload_folder, save_name)

                            file.save(file_path) # 서버에 파일을 진짜로 저장함.

                            # attachments 테이블에 각각 저장
                            sql_file = """INSERT INTO attachments (post_id, origin_name, save_name, file_path)"
                                          VALUES (%s, %s, %s, %s)"""
                            cursor.execute(sql_file, (post_id, origin_name, save_name, file_path))

                conn.commit() # 트랜잭션
                return True

        except Exception as e:
            print(f"Error saving post: {e}")
            conn.rollback()
            return True

        finally:
            conn.close() # save_post(member_id, title, content, files, upload_folder) -> True나 False로 return한다.



