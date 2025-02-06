import os
from contextlib import contextmanager

from flask import Flask, jsonify
from sqlalchemy import create_engine, text

app = Flask(__name__)

PG_HOST = os.environ.get('PG_HOST')
PG_DATABASE = os.environ.get('PG_DATABASE')
PG_USER = os.environ.get('PG_USER')
PG_PASSWORD = os.environ.get('PG_PASSWORD')

engine = create_engine(
    f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:5432/{PG_DATABASE}',
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

@contextmanager
def get_connection():
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()

@app.route('/health/shallow')
def health_shallow():
    return jsonify({"message": "ok"}, 200)

@app.route('/health/deep')
def health_deep():
    with get_connection() as conn:
        try:
            result = conn.execute(text("SELECT NOW();"))
            return jsonify({"db_time": result.fetchone()[0]}, 200)
        except Exception as e:
            return jsonify({"error": str(e)}, 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
