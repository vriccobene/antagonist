from domain import entity


class Author(entity.Entity):
    data_model = {
        "name": str, 
        "author_type": str, 
        "version": int,
    }

    def __iter__(self):
        """
        Return an iterator for the object
        """
        # yield "id", self.id
        for key in self.data_model.keys():
            yield key, getattr(self, key)
