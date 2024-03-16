import uuid
from domain import entity

class SymptomToIncident(entity.Entity):

    data_model = {
        "symptom-id": uuid.UUID,
        "incident-id": uuid.UUID
    }

    def __iter__(self):
        """
        Return an iterator for the object
        """
        for key in self.data_model.keys():
            yield key, str(getattr(self, key))
