"""Contains helper classes and functions for logging"""
import logging
import config

def get_logger(classinstance):
    """
    Returns a logger for this class instance that names the log outputs with
    the fully qualified name of the instance's class
    """
    fullname = '{}.{}.{}'.format(config.ROOTPACKAGE_NAME, classinstance.__module__, classinstance.__class__.__qualname__)
    print(fullname)
    return logging.getLogger(fullname)

def get_baselogger():
    """Creates, configures and returns the base logger for this application package"""
    baselogger = logging.getLogger(config.ROOTPACKAGE_NAME)
    formatter = logging.Formatter(fmt='{levelname}: {message} time:{asctime} name:{name}', style='{')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    baselogger.addHandler(handler)
    baselogger.setLevel(logging.INFO)
    return baselogger
