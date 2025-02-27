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
                if 'files' in request.files:
                    request_data['files'] = request.files.getlist('files')
                validated_data = model(**request_data)
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                logger.error('Validation errors: {}', e.error(), e)
                return jsonify({
                    'error': 'Invalid input',
                }), 400
        return decorated_function
    return decorator
