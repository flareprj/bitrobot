import logging
from datetime import datetime


class MegaHandler(logging.Handler):
    def __init__(self, filename):
        logging.Handler.__init__(self)
        self.filename = filename

    def emit(self, record):
        message = self.format(record)
        with open(self.filename, 'a') as file:
            file.write(message + '\n')


logger_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'std_format': {
            'format': '{asctime} - {levelname} - {name} - {module}:{funcName}:{lineno}- {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format'
        },
        'file': {
            '()': MegaHandler,
            'level': 'DEBUG',
            'filename': f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'handlers': ['file']
            # 'propagate': False
        }
    },

    # 'filters': {},
    # 'root': {}   # '': {}
    # 'incremental': True
}
