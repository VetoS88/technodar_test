"""
    Инициализация приложения
"""
from flask import Flask, g
import psycopg2

app = Flask(__name__)
app.config.from_object('configure')


def connect_db():
    conn = psycopg2.connect(app.config['DATABASE'])
    return conn


def get_db():
    """
    Открывает новое соединение с базой даннных, если его нет в контесте приложения.
    """
    if not hasattr(g, 'pg_db'):
        g.pg_db = connect_db()
    return g.pg_db


@app.teardown_appcontext
def close_db(error):
    """Закрывает содинение сбазой данных"""
    if hasattr(g, 'pg_db'):
        g.pg_db.close()


from src import views
