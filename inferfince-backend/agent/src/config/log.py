import os
import pytz
import socket
from datetime import datetime
import logging.handlers
from logging import Formatter

#按照日志平台的路径与格式
logging.captureWarnings(True)  # 将 warnings 重定向到 logging 系统
hostname = socket.gethostname()
# 日志统一到 backend 根目录 logs/ 下（与 Django 共享）
_base = os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
os.makedirs(_base, exist_ok=True)
log_path = os.path.join(_base, "agent.log")
beijing_tz = pytz.timezone('Asia/Shanghai')


class BeijingFormatter(Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=beijing_tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# 强制规定，日志行格式必须为该格式
log_format = "[%(asctime)s] [%(levelname)s] [%(process)d] [] [] [] %(module)s:%(name)s:%(lineno)d %(message)s"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "beijing_formatter": {
            "()": BeijingFormatter,
            "format": log_format,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "beijing_formatter",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "beijing_formatter",
            "filename": log_path,
            "maxBytes": 500 * 1024 * 1024,  # 500 MB
            "backupCount": 10,
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "py.warnings": {  # 添加对 warnings 的处理
            "level": "WARNING",
            "handlers": ["console", "file"],
            "propagate": False
        },
    },
}
