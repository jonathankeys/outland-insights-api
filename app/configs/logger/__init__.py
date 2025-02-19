import json
import logging
import sys

from loguru import logger

from app.configs.logger.RequestLogHandler import RequestLogHandler


def serialize(record):
    params = {
        "logger": "file_logger",
        "timestamp": record["time"].timestamp(),
        "level": record["level"].name,
    }

    if record["message"] != '':
        params["message"] = record["message"]

    log_param = record["extra"]
    if log_param:
        if "request_id" in log_param:
            params["request_id"] = log_param["request_id"]
        if "method" in log_param:
            params["method"] = log_param["method"]
        if "path" in log_param:
            params["path"] = log_param["path"]
        if "status" in log_param:
            params["status"] = log_param["status"]
        if "ip_address" in log_param:
            params["ip_address"] = log_param["ip_address"]
        if "time" in log_param:
            params["time"] = log_param["time"]

    return json.dumps(params)


def patching(record):
    record["extra"]["serialized"] = serialize(record)


def filter_call_handlers(should_filter: bool):
    return lambda record: should_filter == (record["function"] != "callHandlers")


def create_logger():
    logger.remove(0)
    logger.patch(patching)
    logger.add('logs/application/app_{time}.log', rotation='1 hour', retention='10 days', serialize=True,
               filter=filter_call_handlers(True))
    logger.add('logs/requests/requests_{time}.log', rotation='1 hour', retention='10 days',
               filter=filter_call_handlers(False))

    logger.add(sys.stderr, filter=lambda record: record["function"] not in ["callHandlers", "route_logger_wrapper"])

    return logger


def get_logger():
    return logger


# Update Werkzeug logger to log through Loguru
logging.getLogger("werkzeug").handlers = [RequestLogHandler()]

logger = create_logger()
