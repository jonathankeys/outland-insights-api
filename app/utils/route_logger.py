import time
from functools import wraps

from flask import request, g, jsonify

from app.configs.logger import logger


def route_logger(func):
    @wraps(func)
    def route_logger_wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            with logger.contextualize(request_id=g.get('request_id')):
                response = func(*args, **kwargs)
                endpoint_time = (time.time() - start_time) * 1000
                logger.bind(method=request.method, path=request.path, time=endpoint_time).info('')
                return response
        except Exception as e:
            logger.error('Failed to process request', e)
            return jsonify({'error': 'Internal Server Error'}), 500

    return route_logger_wrapper
