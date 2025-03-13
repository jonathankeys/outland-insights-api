from flask import Blueprint, jsonify
from sqlalchemy import text

from app.configs import logger
from app.models import CreateActivityRequest, CreateActivityResponse, GetActivityResponse, GetRouteResponse
from app.models.routes import GetRouteStatsResponse
from app.utils import get_connection, validate
from app.utils import route_logger

activities = Blueprint('activities', __name__)


@activities.get('/')
@route_logger
def get_activities():
    try:
        with get_connection() as conn:
            result = conn.execute(text('''
                SELECT id, title, description, time_started, time_ended,
                       created_at, updated_at
                FROM activity_log
                ORDER BY created_at DESC
            '''))
            data = []
            for result in result.mappings():
                activity = GetActivityResponse(**result).model_dump()
                data.append(activity)

            return jsonify({
                'data': data,
                'count': len(data)
            }), 200

    except Exception as e:
        logger.error('Failed to fetch all activities', e)
        return jsonify({
            'error': 'Error retrieving activities',
        }), 500


@activities.post('/')
@route_logger
@validate(CreateActivityRequest)
def create_activity(request: CreateActivityRequest):
    try:
        with (get_connection() as conn):
            query = '''
                INSERT INTO activity_log
                (title, description, time_started, time_ended)
                VALUES (:title, :description, :time_started, :time_ended)
                RETURNING id, title, description, time_started, time_ended,
                          created_at, updated_at
            '''
            params = {
                'title': request.title,
                'description': request.description,
                'time_started': request.time_started,
                'time_ended': request.time_ended
            }
            result = conn.execute(text(query), params)
            conn.commit()
            result = result.mappings().first()
            return jsonify({
                'data': CreateActivityResponse(**result).model_dump()
            }), 201

    except Exception as e:
        logger.error('Failed to create activity, input={}', request, e)
        return jsonify({
            'error': 'Error creating activity',
        }), 500


@activities.get('/<activity_id>/routes')
@route_logger
def get_activity_routes(activity_id):
    try:
        with get_connection() as conn:
            results = conn.execute(text('''
                SELECT
                    r.id,
                    r.name,
                    r.description,
                    ST_AsGeoJSON(r.geo)::json as geometry
                FROM
                    routes r
                JOIN activity_routes ar ON
                    ar.route_id = r.id
                WHERE ar.activity_id = :activity_id;
            '''), {'activity_id': activity_id})
            data = []
            for result in results.mappings():
                activity = GetRouteResponse(**result).model_dump()
                data.append(activity)

            return jsonify({
                'data': data,
                'count': len(data)
            }), 200

    except Exception as e:
        logger.error(f'Failed to get all routes from database for activity_id={activity_id}', e)
        return jsonify({
            'error': 'Error retrieving routes for activity'
        }), 500


@activities.get('/<activity_id>')
@route_logger
def get_activity(activity_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text('''
                SELECT id, title, description, time_started, time_ended,
                       created_at, updated_at
                FROM activity_log
                WHERE id = :activity_id
                ORDER BY created_at DESC
            '''), {
                'activity_id': activity_id,
            })

            if result.rowcount > 0:
                data = result.mappings().first()
                return jsonify({
                    'data': GetActivityResponse(**data).model_dump(),
                }), 200
            else:
                return jsonify({
                    'error': 'Activity not found'
                }), 404

    except Exception as e:
        logger.error(f'Failed to get Activity from database for activity_id={activity_id}', e)
        return jsonify({
            'error': 'Error retrieving Activity'
        }), 500


@activities.get('/<activity_id>/routes/<route_id>')
@route_logger
def get_activity_route(activity_id, route_id):
    try:
        with get_connection() as conn:
            params = {
                'activity_id': activity_id,
                'route_id': route_id
            }
            result = conn.execute(text('''
                SELECT
                    r.id,
                    r.name,
                    r.description,
                    ST_AsGeoJSON(r.geo)::json as geometry
                FROM
                    routes r
                JOIN activity_routes ar ON
                    ar.route_id = r.id
                WHERE ar.activity_id = :activity_id
                    AND ar.route_id = :route_id;
            '''), params)

            if result.rowcount > 0:
                data = result.mappings().first()
                return jsonify({
                    'data': GetRouteResponse(**data).model_dump(),
                }), 200
            else:
                return jsonify({
                    'error': 'Route not found'
                }), 404

    except Exception as e:
        logger.error(f'Failed to get route from database for activity_id={activity_id} and route_id={route_id}', e)
        return jsonify({
            'error': 'Error retrieving route for activity'
        }), 500


@activities.get('/<activity_id>/routes/<route_id>/stats')
@route_logger
def get_activity_route_stats(activity_id, route_id):
    try:
        with get_connection() as conn:
            params = {
                'activity_id': activity_id,
                'route_id': route_id
            }
            result = conn.execute(text('''
                    WITH route_data AS (
                        SELECT
                            r.id,
                            r.name,
                            r.description,
                            ST_Simplify(ST_Transform(geo, 26918), 2) AS geo
                        FROM
                            routes r
                        JOIN
                            activity_routes ar ON r.id = ar.route_id
                        WHERE
                            ar.activity_id = :activity_id
                            AND ar.route_id = :route_id
                    ), elevation_points AS (
                        SELECT
                            id,
                            name,
                            description,
                            ST_Z((dp).geom) * 3.28084 AS elevation,
                            LAG(ST_Z((dp).geom) * 3.28084) OVER (PARTITION BY id ORDER BY (dp).path) AS prev_elevation
                        FROM (
                            SELECT
                                id,
                                name,
                                description,
                                ST_DumpPoints(ST_LineMerge(geo)) AS dp
                            FROM route_data
                        ) points
                    ), gains AS (
                        SELECT
                            id,
                            name,
                            description,
                            SUM(
                                CASE
                                    WHEN elevation - prev_elevation > 0
                                    THEN elevation - prev_elevation
                                    ELSE 0
                                END
                            ) AS total_elevation_gain
                        FROM elevation_points
                        GROUP BY id, name, description
                    )
                    SELECT
                        rd.id,
                        rd.name,
                        rd.description,
                        ST_Length(rd.geo) * 3.28084 AS distance,
                        ROUND(ST_ZMin(rd.geo) * 3.28084) AS min_elevation,
                        ROUND(ST_ZMax(rd.geo) * 3.28084) AS max_elevation,
                        ROUND(g.total_elevation_gain) AS total_elevation_gain
                    FROM
                        route_data rd
                    JOIN
                        gains g ON rd.id = g.id;
            '''), params)

            if result.rowcount > 0:
                data = result.mappings().first()
                logger.info(data)
                return jsonify({
                    'data': GetRouteStatsResponse(**data).model_dump(),
                }), 200
            else:
                return jsonify({
                    'error': 'Route not found'
                }), 404

    except Exception as e:
        logger.error(f'Failed to get route from database for activity_id={activity_id} and route_id={route_id}', e)
        logger.error(e)
        return jsonify({
            'error': 'Error retrieving route for activity'
        }), 500
