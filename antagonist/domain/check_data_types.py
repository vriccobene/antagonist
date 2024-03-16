import uuid
from enum import Enum
import datetime as date


class Plane(Enum):
    """ Enumeration for planes """ 
    FORWARDING = "forwarding"
    CONTROL = "control"
    MANAGEMENT = "management"


def check_type(key, value, type):
    """
    Based on the input parameters, invoke the right method below to check the type
    """
    if type == date.datetime:
        return _check_datetime(key, value)
    if type == uuid.UUID:
        return _check_uuid(key, value)
    if type == Plane:
        return _check_plane(key, value)
    return _check_generic(key, value, type)


def _check_generic(key, value, type):
    """ Check if the value is of the correct type """
    if not isinstance(value, type):
        raise ValueError(f"Invalid format key: {key}")
    return value


def _check_plane(key, value):
    """ Check if the plane is valid """
    if value.lower() not in [plane.value.lower() for plane in Plane]:
        raise ValueError(f"Invalid format key: {key}")
    return value.lower()


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
