from domain import annotator
from domain import check_data_types
from domain import entity
import logging
logger = logging.getLogger(__name__)


class NetworkAnomaly(entity.Entity):

    data_model = {
        "description": str, 
        "annotator": annotator.Annotator, 
        "version": int, 
        "state": str
    }

    def __iter__(self):
        """
        Return an iterator for the object
        """
        yield "id", self.id
        for key in self.data_model.keys():
            if key == "annotator":
                yield key, dict(self.annotator)
                continue
            yield key, getattr(self, key)
