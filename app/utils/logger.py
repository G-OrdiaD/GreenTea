import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name):
    """Configure logging without requiring app context"""
    # Create logs directory relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f'{name}.log'),
        maxBytes=1024 * 1024,
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))

    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger.addHandler(file_handler)

    return logger