import os
from contextlib import contextmanager

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text

from GpxExtractor import GpxExtractor

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


@contextmanager
def get_gpx_converter():
    converter = GpxExtractor()
    try:
        yield converter
    finally:
        pass


@app.get('/health/shallow')
def health_shallow():
    return jsonify({"message": "ok"}), 200


@app.get('/health/deep')
def health_deep():
    with get_connection() as conn:
        try:
            result = conn.execute(text("SELECT NOW();"))
            return jsonify({"db_time": result.fetchone()[0]}), 200
        except Exception as e:
            return jsonify({"error": str(e)}, 500)


@app.get('/routes')
def get_routes():
    with get_connection() as conn:
        try:
            query = """
                SELECT 
                    id,
                    name,
                    description,
                    ST_AsGeoJSON(geo)::json as geometry
                FROM routes;
            """
            result = conn.execute(text(query))
            fetched_results = result.fetchall()

            route_list = []
            for route in fetched_results:
                route_dict = {
                    'id': route[0],
                    'name': route[1],
                    'description': route[2],
                    'geo': route[3]
                }
                route_list.append(route_dict)

            return jsonify({'routes': route_list}), 200
        except Exception as e:
            return jsonify({"error": 'Could not retrieve data'}), 500


@app.post('/routes')
def create_route():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get('name')
    description = data.get('description')
    dataset = data.get('dataset')

    if not description or not dataset or not name:
        return jsonify({"error": "Missing required fields"}), 400

    with get_gpx_converter() as gpx:
        try:
            dataset = gpx.extract(dataset)
        except Exception as e:
            return jsonify({"error": 'Could not convert provided dataset'}), 500

    with get_connection() as conn:
        try:
            route_id = insert_route(conn, name, description, dataset)
            conn.commit()
            print(f"Inserted route with ID: {route_id}")
            return jsonify({"id": route_id}), 201

        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500


def insert_route(db_session, name, description, points):
    make_line_str = "ST_MakeLine(ARRAY["
    for i in range(len(points)):
        make_line_str += f"ST_MakePoint(:lon{i}, :lat{i}, :elev{i}, :time{i}),"
    make_line_str = make_line_str[:-1]
    make_line_str += "])::geometry(MULTILINESTRINGZM, 4326)"
    query = f"""
        INSERT INTO routes (name, description, geo)
        SELECT 
            :name,
            :description,
            {make_line_str}
        RETURNING id
    """

    print(query)

    # Create parameters dictionary
    params = {
        "name": name,
        "description": description
    }

    # Add each point's parameters
    for i, (lon, lat, elevation, timestamp) in enumerate(points, 0):
        params[f"lon{i}"] = lon
        params[f"lat{i}"] = lat
        params[f"elev{i}"] = elevation
        params[f"time{i}"] = timestamp

    print(params)

    # Execute the query
    result = db_session.execute(text(query), params)
    return result.scalar()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
