from flask import jsonify, request, Blueprint
from sqlalchemy import text

from app.configs import logger
from app.utils import route_logger, get_connection, get_gpx_converter

routes = Blueprint('routes', __name__)

@routes.get('/')
@route_logger
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
            logger.error('Failed to get all routes from database', e)
            return jsonify({"error": 'Could not retrieve data'}), 500


@routes.post('/')
@route_logger
def create_route():
    data = request.get_json()

    if not data:
        logger.info("No data provided")
        return jsonify({"error": "No data provided"}), 400

    name = data.get('name')
    description = data.get('description')
    dataset = data.get('dataset')

    if not description or not dataset or not name:
        logger.info("Missing required fields: {}, {}, {}", name, description, dataset)
        return jsonify({"error": "Missing required fields"}), 400

    with get_gpx_converter() as gpx:
        try:
            dataset = gpx.extract(dataset)
        except Exception as e:
            logger.error('Failed extract GPX data from input', e)
            return jsonify({"error": 'Could not convert provided dataset'}), 500

    with get_connection() as conn:
        try:
            route_id = insert_route(conn, name, description, dataset)
            conn.commit()
            return jsonify({"id": route_id}), 201
        except Exception as e:
            logger.error('Failed to insert route into database', e)
            return jsonify({"error": str(e)}), 500


def insert_route(db_session, name, description, points):
    logger.info('Inserting route with {} points', len(points))
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

    params = {
        "name": name,
        "description": description
    }

    for i, (lon, lat, elevation, timestamp) in enumerate(points, 0):
        params[f"lon{i}"] = lon
        params[f"lat{i}"] = lat
        params[f"elev{i}"] = elevation
        params[f"time{i}"] = timestamp

    result = db_session.execute(text(query), params)
    return result.scalar()
