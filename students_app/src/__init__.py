from flask import Flask, g
import psycopg2

app = Flask(__name__)
app.config.from_object('config')


def connect_db():
    """Connects to database."""
    conn = psycopg2.connect(app.config['DATABASE'])
    return conn


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'pg_db'):
        g.pg_db = connect_db()
    return g.pg_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'pg_db'):
        g.pg_db.close()


from src import views
