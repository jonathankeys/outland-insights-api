from flask import Blueprint, jsonify
from sqlalchemy import text

from app.configs import logger
from app.models import CreateActivityRequest, CreateActivityResponse, GetActivityResponse, GetRouteResponse
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
        with get_connection() as conn:
            query = text('''
                INSERT INTO activity_log
                (title, description, time_started, time_ended)
                VALUES (:title, :description, :time_started, :time_ended)
                RETURNING id, title, description, time_started, time_ended,
                          created_at, updated_at
            ''')
            params = {
                'title': request.title,
                'description': request.description,
                'time_started': request.time_started,
                'time_ended': request.time_ended
            }
            result = conn.execute(query, params).mappings().first()
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
        logger.error(e)
        return jsonify({
            'error': 'Error retrieving route for activity'
        }), 500
