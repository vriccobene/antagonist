import uuid
from enum import Enum
import datetime as date


def check_type(key, value, type):
    """
    Based on the input parameters, invoke the right method below to check the type
    """
    if type == date.datetime:
        return _check_datetime(key, value)
    if type == uuid.UUID:
        return _check_uuid(key, value)
    return _check_generic(key, value, type)


def _check_generic(key, value, type):
    """ Check if the value is of the correct type """
    if not isinstance(value, type):
        raise ValueError(f"Invalid format key: {key}")
    return value


def _check_datetime(key, value):
    """ Check if the input string is a valid datetime """
    try:
        value = date.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValueError(f"Invalid format key: {key}")  
    return value


def _check_uuid(key, value):
    """ Check if the input string is a valid UUID """
    try:
        value = uuid.UUID(value)
    except ValueError:
        raise ValueError(f"Invalid format key: {key}")
    return value
