import logging.config
import pprint

from modules.settings import *
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
    sleep(randint(1, 8))


def is_internet():
    url = 'https://www.google.com'
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        print('Сouldnt restore the connection, trying again..')
        logger.exception('Сouldnt restore the connection, trying again..', exc_info=True)
        sleep_()
        return False
    except Exception as e:
        print('Another exception on unstable connection!', e)
        logger.exception('Another exception on unstable connection!', e, exc_info=True)
    else:
        print('Connection is ok now! Continue trade..')
        logger.info('Connection is ok now! Continue trade..')
        return True


def exx(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ValueError as e:
            logger.exception(f'ValueError: {e}', exc_info=True)
            sleep_()
        except KeyError as e:
            logger.exception(f'KeyError: {e}', exc_info=True)
            sleep_()
        except TypeError as e:
            logger.exception(f'TypeError: {e}', exc_info=True)
            sleep_()
        except IndexError as e:
            logger.exception(f'IndexError: {e}', exc_info=True)
            sleep_()
        except (ConnectionError, TimeoutError) as e:
            logger.exception(f'ConnectionError, TimeoutError: {e}', exc_info=True)
            print('\nUnstable connection! Start reconnecting..')
            while not is_internet():
                is_internet()
            else:
                result = func(*args, **kwargs)
                return result
        except urllib3.exceptions.ProtocolError as e:
            logger.exception(f'ProtocolError: {e}', exc_info=True)
            sleep_()
        except bravado.exception.HTTPBadRequest as e:
            logger.exception(f'HTTPBadRequest: {e}', exc_info=True)
            sleep_()
        except bravado.exception.HTTPGatewayTimeout as e:
            logger.exception(f'HTTPGatewayTimeout: {e}', exc_info=True)
            sleep_()
        except bravado.exception.HTTPBadGateway as e:
            logger.exception(f'HTTPBadGateway: {e}', exc_info=True)
            sleep_()
        except bravado.exception.BravadoTimeoutError as e:
            logger.exception(f'BravadoTimeoutError: {e}', exc_info=True)
            sleep_()
        except bravado.exception.BravadoConnectionError as e:
            logger.exception(f'BravadoConnectionError: {e}', exc_info=True)
            sleep_()
        except bravado.exception.HTTPInternalServerError as e:
            logger.exception(f'HTTPInternalServerError: {e}', exc_info=True)
            sleep_()
        except bravado_core.exception.MatchingResponseNotFound as e:
            logger.exception(f'MatchingResponseNotFound: {e}', exc_info=True)
            sleep_()
        except bravado_core.exception.SwaggerMappingError as e:
            logger.exception(f'SwaggerMappingError: {e}', exc_info=True)
            sleep_()
        except requests.exceptions.ConnectionError as e:
            logger.exception(f'ConnectionError: {e}', exc_info=True)
            sleep_()
        except urllib3.exceptions.NewConnectionError as e:
            logger.exception(f'NewConnectionError: {e}', exc_info=True)
            sleep_()
        except urllib3.exceptions.MaxRetryError as e:
            logger.exception(f'MaxRetryError: {e}', exc_info=True)
            sleep_()
        except Exception as e:
            logger.error(f'Exception: {e}', exc_info=True)
            sleep_()
        else:
            return result

    return wrapper
