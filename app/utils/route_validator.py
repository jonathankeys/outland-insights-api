from functools import wraps
from typing import Callable

from flask import request, jsonify
from pydantic import ValidationError
from app.configs import logger


def validate(model) -> Callable:
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                request_data = request.get_json() if request.is_json else request.form.to_dict()
                validated_data = model(**request_data)
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                logger.error('Validation error: {}', e)
                return jsonify({
                    'error': 'Validation of input failed.',
                    'message': e.errors()
                }), 400
        return decorated_function
    return decorator
