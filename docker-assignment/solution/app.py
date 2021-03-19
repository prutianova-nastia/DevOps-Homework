from flask import Flask, request, Response
import psycopg2
import time

app = Flask(__name__)


def connect():
    app.conn = psycopg2.connect(
        host="database",
        user="postgres",
        database="postgres",
        password="password",
        port="5432")
    app.cursor = app.conn.cursor()

def create_table():
    sql = '''
    CREATE TABLE IF NOT EXISTS MyTable (
    key text NOT NULL,
    value DOUBLE PRECISION
    );'''
    app.cursor.execute(sql)
    app.conn.commit()

    sql = '''
    CREATE TABLE IF NOT EXISTS BackupTable (
    key text NOT NULL PRIMARY KEY,
    value DOUBLE PRECISION
    );'''
    app.cursor.execute(sql)
    app.conn.commit()


def insert(key, value):
    sql = "INSERT INTO MyTable (key, value) VALUES ('{}', '{}')".format(key, value)
    app.cursor.execute(sql)
    app.conn.commit()

def get_average():
    sql = '''
    SELECT AVG(value) FROM MyTable;
    '''
    app.cursor.execute(sql)
    average = app.cursor.fetchall()[0][0]
    if average is None:
        average = 0

    sql = "INSERT INTO BackupTable (key, value) VALUES ('{}', '{}')".format("return", average)
    sql += " on conflict (key) do update set (key, value) = (excluded.key, excluded.value)"
    app.cursor.execute(sql)
    app.conn.commit()

    return average

@app.route('/submit', methods=["POST"])
def submit():
    input = request.data.decode("utf-8")
    key, value = input.split(" ")
    insert(key, value)
    return Response("", status=201, mimetype='application/json')

@app.route('/avg', methods=["GET"])
def avg():
    return Response(str(get_average()), status=200, mimetype='application/json')

@app.route('/drop', methods=["GET"])
def drop():
    sql = "DROP TABLE MyTable;"
    app.cursor.execute(sql)
    app.conn.commit()
    sql = "DROP TABLE BackupTable;"
    app.cursor.execute(sql)
    app.conn.commit()
    create_table()
    return Response(0, status=200, mimetype='application/json')


if __name__ == '__main__':
    connected = False
    while not connected:
        try:
            connect()
            connected = True
        except:
            time.sleep(1)
    app.logger.debug("Connected to DB")

    create_table()
    app.logger.debug("Created table")

    app.run(debug=True, host='0.0.0.0', port=5000)
