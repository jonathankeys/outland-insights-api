from decouple import config
from flask import Flask

from app.configs import logger, engine
from app.endpoints import routes, health
from app.extractors.GpxExtractor import GpxExtractor
from app.utils import route_logger, get_connection, get_gpx_converter, register_request_handlers

app = Flask(__name__)
app.logger.disabled = True

# Add handlers for each request
register_request_handlers(app)

# Do not allow file uploads over 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Add endpoints
app.register_blueprint(health, url_prefix='/health')
app.register_blueprint(routes, url_prefix='/routes')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config('APP_PORT', cast=int))
