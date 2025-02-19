from contextlib import contextmanager

from app.configs import engine
from app.extractors.GpxExtractor import GpxExtractor


@contextmanager
def get_connection():
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_gpx_converter():
    converter = GpxExtractor()
    try:
        yield converter
    finally:
        pass