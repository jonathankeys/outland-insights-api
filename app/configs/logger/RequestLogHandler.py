import logging

from loguru import logger


class RequestLogHandler(logging.Handler):
    def emit(self, record):
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).info(record.getMessage())
