import logging.config
from modules.settings import logger_config
from random import randint
from time import sleep
import bravado
import bravado_core
import requests
import urllib3
from bravado import exception
from bravado_core import exception

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')


def sleep_():
    sleep(randint(1, 5))


def is_internet():
    url = 'https://www.google.com'
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        print('Сouldnt restore the connection, trying again..')
        sleep_()
        return False
    except Exception as e:
        print('Another exception on unstable connection!', e)
    else:
        print('Connection is ok now! Continue trade..')
        return True


def exx(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ValueError as e:
            logger.exception(f'ValueError: {e}')
            sleep_()
        except KeyError as e:
            logger.exception(f'KeyError: {e}')
            sleep_()
        except TypeError as e:
            logger.exception(f'TypeError: {e}')
            sleep_()
        except IndexError as e:
            logger.exception(f'IndexError: {e}')
            sleep_()
        except (ConnectionError, TimeoutError) as e:
            logger.exception(f'ConnectionError, TimeoutError: {e}')
            print('\nUnstable connection! Start reconnecting..')
            while not is_internet():
                is_internet()
            else:
                result = func(*args, **kwargs)
                return result
        except urllib3.exceptions.ProtocolError as e:
            logger.exception(f'ProtocolError: {e}')
            sleep_()
        except bravado.exception.HTTPBadRequest as e:
            logger.exception(f'HTTPBadRequest: {e}')
            sleep_()
        except bravado.exception.HTTPGatewayTimeout as e:
            logger.exception(f'HTTPGatewayTimeout: {e}')
            sleep_()
        except bravado.exception.HTTPBadGateway as e:
            logger.exception(f'HTTPBadGateway: {e}')
            sleep_()
        except bravado.exception.BravadoTimeoutError as e:
            logger.exception(f'BravadoTimeoutError: {e}')
            sleep_()
        except bravado.exception.BravadoConnectionError as e:
            logger.exception(f'BravadoConnectionError: {e}')
            sleep_()
        except bravado.exception.HTTPInternalServerError as e:
            logger.exception(f'HTTPInternalServerError: {e}')
            sleep_()
        except bravado_core.exception.MatchingResponseNotFound as e:
            logger.exception(f'MatchingResponseNotFound: {e}')
            sleep_()
        except bravado_core.exception.SwaggerMappingError as e:
            logger.exception(f'SwaggerMappingError: {e}')
            sleep_()
        except requests.exceptions.ConnectionError as e:
            logger.exception(f'ConnectionError: {e}')
            sleep_()
        except urllib3.exceptions.NewConnectionError as e:
            logger.exception(f'NewConnectionError: {e}')
            sleep_()
        except urllib3.exceptions.MaxRetryError as e:
            logger.exception(f'MaxRetryError: {e}')
            sleep_()
        else:
            return result

    return wrapper
