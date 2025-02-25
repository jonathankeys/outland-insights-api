from flask import Blueprint
from flask import jsonify
from sqlalchemy import text

from app.configs import logger
from app.models import CreateActivityRequest, CreateActivityResponse
from app.utils import get_connection, validate
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
@validate(CreateActivityRequest)
def create_activity(request: CreateActivityRequest):
    try:
        with get_connection() as conn:
            query = text("""
                INSERT INTO activity_log
                (title, description, time_started, time_ended)
                VALUES (:title, :description, :time_started, :time_ended)
                RETURNING id, title, description, time_started, time_ended,
                          created_at, updated_at
            """)
            params = {
                "title": request.title,
                "description": request.description,
                "time_started": request.time_started,
                "time_ended": request.time_ended
            }
            db_result = conn.execute(query, params).fetchone()
            return jsonify({
                'message': 'Activity created successfully',
                'activity': CreateActivityResponse(**db_result._mapping).model_dump()
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
