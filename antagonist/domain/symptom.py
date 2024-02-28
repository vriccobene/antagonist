import uuid
import datetime as date
from domain import data_types

import logging
logger = logging.getLogger(__name__)


class Symptom:

    # Define the properties I want to have and their types, to be used for validation
    data_model = {
        "event-id": uuid.UUID,
        "start-time": date.datetime, 
        "end-time": date.datetime, 
        "description": str, 
        "confidence-score": float, 
        "concern-score": float, 
        "plane": data_types.Plane, 
        "condition": str,
        "action": str, 
        "cause": str, 
        "pattern": str, 
        "source-type": str, 
        "source-name": str,
        "tags": dict
    }
    
    def __init__(self, args):
        """
        Validate the input and initialize the object
        """
        for key in list(self.data_model.keys()):
            setattr(self, key, None) 
        self._validate_and_initialize(args)

    def _validate_and_initialize(self, args):
        """
        Validate the kwargs passed to the constructor and initialize the object
        """
        for key, value in args.items():
            logger.debug(f"Validating {key} with value {value}")
            if key not in self.data_model:
                raise ValueError(f"Invalid property: {key}")
            else:
                formatted_val = data_types.check_type(key, value, self.data_model[key])
                setattr(self, key, formatted_val)

    def to_dict(self):
        return self.__dict__
    
    def get_field_keys(self):
        """
        Return the fields of the object that require to be store in the database
        """
        res = list(self.data_model.keys())
        res.remove("tags")
        return res
    
    def get_field_values(self):
        """
        Return the values of the fields of the object that require to be store in the database
        """
        res = [getattr(self, key) for key in self.data_model.keys()]
        res = res[:-1]
        return res
    