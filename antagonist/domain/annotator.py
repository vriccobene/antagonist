from domain import entity


class Annotator(entity.Entity):
    data_model = {
        "name": str, 
        "annotator_type": str, 
    }

    def __iter__(self):
        """
        Return an iterator for the object
        """
        # yield "id", self.id
        for key in self.data_model.keys():
            yield key, getattr(self, key)
