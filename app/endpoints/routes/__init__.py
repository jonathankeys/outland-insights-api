from flask import jsonify, Blueprint
from sqlalchemy import text

from app.configs import logger
from app.models import (GetRouteResponse, CreateRouteRequest, CreateRouteResponse,
                        UploadRouteRequest, UploadRouteResponse)
from app.utils import route_logger, get_connection, get_gpx_converter, validate

routes = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {'gpx', 'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.get('/')
@route_logger
def get_routes():
    with get_connection() as conn:
        try:
            query = '''
                SELECT
                    id,
                    name,
                    description,
                    ST_AsGeoJSON(geo)::json as geometry
                FROM routes;
            '''
            results = conn.execute(text(query))
            data = []
            for result in results.mappings():
                activity = GetRouteResponse(**result).model_dump()
                data.append(activity)

            return jsonify({
                'data': data,
                'count': len(data)
            }), 200
        except Exception as e:
            logger.error('Failed to get all routes', e)
            return jsonify({
                'error': 'Error getting routes'
            }), 500


@routes.post('/file')
@route_logger
@validate(UploadRouteRequest)
def upload_route(request: UploadRouteRequest):
    with get_gpx_converter() as gpx, get_connection() as conn:
        try:
            results = []
            for file in request.files:
                if file and allowed_file(file.filename):
                    content = file.stream.read().decode('utf-8')
                    dataset = ' '.join(line.strip() for line in content.splitlines() if line.strip())
                    try:
                        dataset = gpx.extract(dataset)
                    except Exception as e:
                        logger.error('Failed extract GPX data from input, request={}', request, e)
                        return jsonify({
                            'error': 'Could not convert provided dataset into valid format'
                        }), 500
                    try:
                        result = insert_route(conn, request.name, request.description, dataset)
                        results.append(UploadRouteResponse(**result).model_dump())
                    except Exception as e:
                        logger.error('Failed to insert route into database, {} files processed successfully. Input={}',
                                     len(results), request, e)
                        return jsonify({
                            'error': 'Error uploading file(s)'
                        }), 500
            return jsonify({
                'count': len(results),
                'data': results
            }), 201
        except Exception as e:
            logger.error('Failed to upload file(s), input={}', request, e)
            return jsonify({
                'error': 'Error uploading file(s)'
            }), 500


@routes.post('/')
@route_logger
@validate(CreateRouteRequest)
def create_route(request: CreateRouteRequest):
    with get_gpx_converter() as gpx:
        try:
            dataset = gpx.extract(request.dataset)
        except Exception as e:
            logger.error('Failed extract GPX data from input, request={}', request, e)
            return jsonify({
                'error': 'Could not convert provided dataset into valid format'
            }), 500

    with get_connection() as conn:
        try:
            result = insert_route(conn, request.name, request.description, dataset)
            return jsonify({
                'data': CreateRouteResponse(**result).model_dump()
            }), 201
        except Exception as e:
            logger.error('Failed to insert route, input={}', request, e)
            return jsonify({
                'error': 'Error uploading route'
            }), 500


def insert_route(db_session, name, description, points):
    logger.info('Inserting route with {} points', len(points))
    make_line_str = 'ST_MakeLine(ARRAY['
    for i in range(len(points)):
        make_line_str += f'ST_MakePoint(:lon{i}, :lat{i}, :elev{i}, :time{i}),'
    make_line_str = make_line_str[:-1]
    make_line_str += '])::geometry(MULTILINESTRINGZM, 4326)'
    query = f'''
        INSERT INTO routes (name, description, geo)
        SELECT
            :name,
            :description,
            {make_line_str}
        RETURNING id, name, description, ST_AsGeoJSON(geo)::json as geometry
    '''

    params = {
        'name': name,
        'description': description
    }

    for i, (lon, lat, elevation, timestamp) in enumerate(points, 0):
        params[f'lon{i}'] = lon
        params[f'lat{i}'] = lat
        params[f'elev{i}'] = elevation
        params[f'time{i}'] = timestamp

    result = db_session.execute(text(query), params)
    return result.mappings().first()
