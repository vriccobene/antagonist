from domain import check_data_types

import logging
logger = logging.getLogger(__name__)


class Entity:

    def __init__(self, args):
        """
        Validate the input and initialize the object
        """
        self.id = None
        for key in list(self.data_model.keys()):
            setattr(self, key, None) 
        self._validate_and_initialize(args)

    def _validate_and_initialize(self, args):
        """
        Validate the args passed to the constructor and initialize the object
        """
        for key, value in args.items():
            logger.debug(f"Validating {key} with value {value}")
            if key not in self.data_model:
                raise ValueError(f"Invalid property: {key}")
            else:
                if issubclass(self.data_model[key], Entity):
                    formatted_val = self.data_model[key](value)
                else:
                    formatted_val = check_data_types.check_type(key, value, self.data_model[key])
                setattr(self, key, formatted_val)

    def get_field_keys(self):
        """
        Return the fields of the object that require to be store in the database
        """
        res = list(self.data_model.keys())
        return res
    
    def get_field_values(self):
        """
        Return the values of the fields of the object that require to be store in the database
        """
        res = [getattr(self, key) for key in self.data_model.keys()]
        return res
