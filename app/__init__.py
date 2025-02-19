import uuid

from decouple import config
from flask import Flask, request, g

from app.configs import logger, engine
from app.endpoints import routes, health
from app.extractors.GpxExtractor import GpxExtractor
from app.utils import route_logger, get_connection, get_gpx_converter

app = Flask(__name__)
app.logger.disabled = True
app.register_blueprint(health, url_prefix='/health')
app.register_blueprint(routes, url_prefix='/routes')


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config('APP_PORT', cast=int))
