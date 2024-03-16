from domain import check_data_types
from domain import author, entity
import logging
logger = logging.getLogger(__name__)


class Incident(entity.Entity):

    data_model = {
        "description": str, 
        "author": author.Author, 
        "version": int, 
        "state": str
    }

    def __iter__(self):
        """
        Return an iterator for the object
        """
        yield "id", self.id
        for key in self.data_model.keys():
            if key == "author":
                yield key, dict(self.author)
                continue
            yield key, getattr(self, key)
