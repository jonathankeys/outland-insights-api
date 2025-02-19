import uuid

from flask import g, request

def register_request_handlers(app):
    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            request_id = str(uuid.uuid4())
        g.request_id = request_id

    @app.after_request
    def after_request(response):
        response.headers['X-Request-ID'] = g.get('request_id')
        return response