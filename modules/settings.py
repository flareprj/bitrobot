import configparser
import logging


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
            'filename': 'debug.log',
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


class Settings:
    def __init__(self, filename):
        self.config = configparser.ConfigParser()
        self.config.read(filename)

        self.api_key = self.config["Keys"]["api_key"]
        self.secret_key = self.config["Keys"]["secret_key"]
        self.symbol = self.config["Parameters"]["symbol"]
        self.strategy = self.config["Parameters"]["strategy"]

    def update(self, name):
        self.config.set("Parameters", "strategy", name)
