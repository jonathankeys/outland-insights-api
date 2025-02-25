from flask import Blueprint, request, jsonify
from sqlalchemy import text

from app.configs import logger
from app.utils import get_connection
from app.utils import route_logger

activities = Blueprint('activities', __name__)


@activities.get('/')
@route_logger
def get_activities():
    try:
        with get_connection() as conn:
            result = conn.execute(text("""
                SELECT id, title, description, time_started, time_ended,
                       created_at, updated_at
                FROM activity_log
                ORDER BY created_at DESC
            """))
            fetched_results = result.fetchall()

            activities_list = [{
                'id': activity[0],
                'title': activity[1],
                'description': activity[2],
                'time_started': activity[3].isoformat() if activity[3] else None,
                'time_ended': activity[4].isoformat() if activity[4] else None,
                'created_at': activity[5].isoformat() if activity[5] else None,
                'updated_at': activity[6].isoformat() if activity[6] else None
            } for activity in fetched_results]

            return jsonify({
                'activities': activities_list,
                'count': len(activities_list)
            }), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch activities',
            'message': str(e)
        }), 500


@activities.post('/')
@route_logger
def create_activity():
    try:
        data = request.get_json()

        # Add validation library through #20
        required_fields = ['title', 'time_started']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Validation error',
                    'message': f'Missing required field: {field}'
                }), 400

        if len(data['title']) < 3:
            return jsonify({
                'error': 'Validation error',
                'message': 'Title must be at least 3 characters long'
            }), 400

        try:
            time_started = data['time_started']
            time_ended = data['time_ended'] if 'time_ended' in data and data['time_ended'] else None
            if time_ended and time_ended <= time_started:
                return jsonify({
                    'error': 'Validation error',
                    'message': 'End time must be after start time'
                }), 400

        except (ValueError, TypeError):
            return jsonify({
                'error': 'Validation error',
                'message': 'Invalid datetime format. Please use ISO 8601 format'
            }), 400

        with get_connection() as conn:
            new_activity = conn.execute(text("""
                INSERT INTO activity_log
                (title, description, time_started, time_ended)
                VALUES (:title, :description, :time_started, :time_ended)
                RETURNING id, title, description, time_started, time_ended,
                          created_at, updated_at
            """), {
                "title": data['title'],
                "description": data.get('description'),
                "time_started": time_started,
                "time_ended": time_ended
            }).fetchone()

            logger.info(f"New activity created: {new_activity}")
            conn.commit()

            return jsonify({
                'message': 'Activity created successfully',
                'activity': {
                    'id': new_activity[0],
                    'title': new_activity[1],
                    'description': new_activity[2],
                    'time_started': new_activity[3].isoformat() if new_activity[3] else None,
                    'time_ended': new_activity[4].isoformat() if new_activity[4] else None,
                    'created_at': new_activity[5].isoformat() if new_activity[5] else None,
                    'updated_at': new_activity[6].isoformat() if new_activity[6] else None
                }
            }), 201

    except Exception as e:
        return jsonify({
            'error': 'Failed to create activity',
            'message': str(e)
        }), 500


@activities.get('/<activity_id>/routes')
@route_logger
def get_activity_routes(activity_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("""
                SELECT
                    r.id,
                    r.name,
                    r.description,
                    ST_AsGeoJSON(r.geo)::json as geometry
                FROM
                    routes r
                JOIN activity_routes ar ON
                    ar.route_id = r.id
                    AND ar.activity_id = :activity_id;
            """), {"activity_id": activity_id})
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
        logger.error(f'Failed to get all routes from database for activity_id={activity_id}', e)
        logger.error(e)
        return jsonify({"error": 'Could not retrieve data'}), 500
