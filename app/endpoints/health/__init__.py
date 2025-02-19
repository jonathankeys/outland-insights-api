from flask import jsonify, Blueprint
from sqlalchemy import text

from app.configs import logger
from app.utils import route_logger, get_connection

health = Blueprint('health', __name__)


@health.get('/shallow')
@route_logger
def health_shallow():
    logger.info("Health check requested")
    return jsonify({"message": "ok"}), 200


@health.get('/deep')
@route_logger
def health_deep():
    with get_connection() as conn:
        try:
            logger.info("Deep health check requested")
            result = conn.execute(text("SELECT NOW();"))
            return jsonify({"db_time": result.fetchone()[0]}), 200
        except Exception as e:
            logger.error('Failed to connect to database', e)
            return jsonify({"error": "Failed health check"}, 500)
