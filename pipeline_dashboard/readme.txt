

��� �������� ������������ �� UBUNTU.

1. ��������� ����������� ���������� �� ����� requirements.txt

pip3 install -r requirements.txt

2. ��������� postgreSQL.

sudo apt update 
sudo apt install postgresql postgresql-contrib 

sudo service postgresql start
service postgresql status  #��������� - 'online'

3. �������� ����.

createdb zen --encoding='utf-8'

4. �������� ������������ �������� ����


CREATE USER my_user2 WITH ENCRYPTED PASSWORD 'my_user_password';
GRANT ALL PRIVILEGES ON DATABASE zen TO my_user2;
GRANT USAGE, SELECT ON SEQUENCE zen  TO my_user2;
\q

5. �������� �� ������ (����� ��������� � ������)

pg_restore -d zen zen.dump

6. �������� ������������ ������ 

sudo su postgres
psql -d zen

CREATE TABLE dash_visits(record_id serial PRIMARY KEY,       
                         item_topic VARCHAR(128),
                         source_topic VARCHAR(128),
                         age_segment VARCHAR(128),
                         dt TIMESTAMP,
                         visits INT);

CREATE TABLE dash_engagement (record_id serial PRIMARY KEY, 
                             dt TIMESTAMP,        
                             item_topic VARCHAR(128),     
                             event VARCHAR(128),    
                             age_segment VARCHAR(128),
                             unique_users BIGINT);
\q

GRANT USAGE, SELECT ON SEQUENCE dash_visits TO my_user2;

GRANT USAGE, SELECT ON SEQUENCE dash_engagement TO my_user2;

7. ������ ������� (��������� � ������)

python3 pipeline.py -s '2010-01-01' -e '2020-12-31'

8. ������ �������� (��������� � ������)

python3 dash_zen_last.py

9. ��� ������� ����������� � �������� �� ������

http://x.x.x.x:3000/

������ �.�.�.� - ���� ����������� ������


