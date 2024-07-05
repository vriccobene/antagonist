import uuid
import json
import datetime as date
from domain import entity, check_data_types
from domain import annotator

import logging
logger = logging.getLogger(__name__)


class Symptom(entity.Entity):

    # Define the properties I want to have and their types, to be used for validation
    data_model = {
        "event-id": uuid.UUID,
        "start-time": date.datetime, 
        "end-time": date.datetime, 
        "description": str, 
        "confidence-score": float, 
        "concern-score": float,  
        "pattern": str, 
        "annotator": annotator.Annotator, 
        "tags": dict
    }

    def __init__(self, args):
        if not args.get('even-id', None):
            args['event-id'] = str(uuid.uuid4())
        
        try:
            start_time = int(args.get('start-time', None)[:10])
            args['start-time'] = str(date.datetime.fromtimestamp(start_time)).replace(" ", "T")
        except ValueError:
            pass
        
        try:
            end_time = int(args.get('end-time', None)[:10])
            args['end-time'] = str(date.datetime.fromtimestamp(end_time)).replace(" ", "T")
        except ValueError:
            pass

        if isinstance(args.get('confidence-score', None), int):
            args['confidence-score'] = float(args.get('confidence-score', None))

        if isinstance(args.get('concern-score', None), int):
            args['concern-score'] = float(args.get('concern-score', None))

        logger.info(f"ARG TAGS: {args.get('tags', None)}")
        if isinstance(args.get('tags', None), str):
            args['tags'] = json.loads(args.get('tags', '{}').replace("'", '"'))

        super().__init__(args)

    def __iter__(self):
        """
        Return an iterator for the object
        """
        yield "id", self.id
        # for key in self.data_model.keys():
        #     yield key, getattr(self, key)
        
        for key in self.data_model.keys():
            if key == "annotator":
                yield key, dict(self.annotator)
                continue
            yield key, getattr(self, key)
    
    def get_field_keys(self):
        """
        Return the fields of the object that require to be store in the database
        """
        res = list(self.data_model.keys())
        res.remove("tags")
        res.remove("annotator")
        return res
    
    def get_field_values(self):
        """
        Return the values of the fields of the object that require to be store in the database
        """
        res = [getattr(self, key) for key in self.data_model.keys() if key not in ['annotator', 'tags']]
        # res = res[:-2]
        return res
    