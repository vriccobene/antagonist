from domain import author
import logging
logger = logging.getLogger(__name__)


class Incident:

    data_model = {
        "description": str, 
        "author": author.Author, 
        "version": int, 
        "state": str
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
        Validate the args passed to the constructor and initialize the object
        """
        for key, value in args.items():
            logger.debug(f"Validating {key} with value {value}")
            if key not in self.data_model:
                raise ValueError(f"Invalid property: {key}")
            else:
                formatted_val = data_types.check_type(key, value, self.data_model[key])
                setattr(self, key, formatted_val)
