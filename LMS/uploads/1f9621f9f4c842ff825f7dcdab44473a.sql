select @@hostname; 

-- 이 창은 메모장처럼 사용됨.
-- 스크립트를 1줄씩 실행하는 것이 기본 (ctrl + enter)
-- 만약 더미데이터를 20개 입력한다. (블럭설정 ctrl + shift + enter)

use sakila; -- sakila 데이터베이스에 가서 사용할 것
select * from actor; -- actor 테이블에 모든 값 가져와.

use world; -- world 데이터베이스에 가서 사용할 것.
select * from city; -- city 라는 테이블에 모든 값을 가져와.
 
 CREATE DATABASE DOItSQL;
 DROP DATABASE DOItSQL;
 
CREATE DATABASE dotisql; -- 생성
DROP DATABASE dotisql; -- 삭제
USE dotisql; 


CREATE TABLE doti_create_table (
col_1 INT, 
col_2 VARCHAR(50), -- var 를 붙이면 가변이라는 뜻. 무조건 50칸을 차지하지 않음. 
col_3 DATETIME
);

-- DROP 문으로 이용한 테이블 삭제
DROP TABLE doti_create_table;

-- INSERT 문으로 데이터 삽입
CREATE TABLE doti_dml (
col_1 INT,
col_2 VARCHAR(50),
col_3 DATETIME
);
INSERT INTO doit_dml (col_1, col_2, col_3) VALUES (1, 'DoItSQL', '2023-01-01');

DROP TABLE IF EXISTS doit_dml; -- 파일이 있는지 확인문.
CREATE TABLE doit_dml (
col_1 INT,
col_2 VARCHAR(50),
col_3 DATETIME
);

INSERT INTO doit_dml (col_1, col_2, col_3) VALUES (1, 'DoItSQL', '2023-01-01');

-- 데이터 입력 결과 확인
SELECT * FROM doit_dml;

INSERT INTO doit_dml(col_1) VALUES ('문자 입력'); -- 데이터 오류 발생 시 예시alte

INSERT INTO doit_dml VALUES (2, '열 이름 생략', '2023-01-02');   -- 열 이름 생략하고 데이터 삽입 
SELECT * FROM doit_dml;  -- 삽입된 데이터 확인
INSERT INTO doit_dml VALUES (3, 'col_3 값 생략'); -- 열 개수 불일치로 인한 오류 발생 예시

INSERT INTO doit_dml(col_1, col_2) VALUES (3, 'col_3 값 생략');
SELECT * FROM doit_dml;

-- 삽입할 데이터 순서 변경alter
INSERT INTO doit_dml(col_1, col_3, col_2) VALUES (4, '2023-01-03', '열 순서 변경');
SELECT * FROM doit_dml;

-- 여러 데이터 한 번에 삽입
INSERT INTO doit_dml (col_1, col_2, col_3)
VALUES (5, '데이터 입력5', '2023-01-03'), (6, '데이터 입력6', '2023-01-03'), (7, '데이터 입력7', '2023-01-03');
SELECT * FROM doit_dml;

-- DROP TABLE IF EXISTS doit_dml;

-- AUTO INCREMENT 설정이 추가된 테이블 생성
-- CREATE TABLE doit_dml(
-- col_1 INT AUTO_INCREMENT,
-- col_2 VARCHAR(50),
-- col_3 DATETIME,
-- PRIMARY KEY (col_1)       -- col_1을 기본키로 지정(필수값)
-- );

-- 데이터 넣기. , col_1은 이제 아예 빼고 생략하고 입력해도 됨.
-- INSERT INTO doit_dml (col_2, col_3) VALUES ('첫 번째 데이터', '2023-01-01');
-- INSERT INTO doit_dml (col_2, col_3) VALUES ('두 번째 데이터', '2023-01-02');
-- INSERT INTO doit_dml (col_2, col_3) VALUES ('세 번째 데이터', '2023-01-03');

-- 데이터 결고ㅏ 확인
-- SELECT * FROM doit_dml;

-- NULL 을 허용하지 않는 테이블 생성 후 NULL 삽입 시 오류가 발생한 예
CREATE TABLE doit_notnull (
col_1 INT,
col_2 VARCHAR(50) NOT NULL  -- NULL 허용하지 않음.
);

INSERT INTO doit_notnull (col_1) VALUES (1);

-- update 문으로 데이터 수정1
UPDATE doit_dml SET col_2 = '데이터 수정'
WHERE col_1 = 4;

-- update 문으로 데이터 수정2
UPDATE doit_dml SET col_2 = '데이터 수정'
WHERE col_1 = 4;

-- update 문으로 데이터 전체 데이터 수정
UPDATE doit_dml SET col_1 = col_1 + 10;

-- delete 문의 기본 형식
-- DELETE FROM 테이블 이름 WHERE [열 = 조건]
DELETE FROM doit_dml WHERE col_1 = 14;

-- delete 문으로 테이블 전체 데이터 삭제
DELETE FROM doit_dml;

CREATE TABLE doit_exam_t1

/* 
작성자 : 홍길동
작성일 : 2026-01-27
설명 : DOit_exam DB의 테이블을 생성하는 쿼리이다.
*/

-- 스키마(Schemas) 란 데이터베이스의 구조와 제약 조건에 대하여 전반적인 명세를 기술.
-- 즉, 데이터베이스를 구성하는 자료 개체의 성질, 관계, 조작, 자료값 등의 정의를 총칭.

