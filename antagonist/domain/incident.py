class Incident:
    def __init__(
            self, id=None, start_time=None, end_time=None, 
            descript=None, source_type=None, source_name=None):

        self._id = id
        self._start_time = start_time
        self._end_time = end_time
        self._descript = descript
        self._source_type = source_type
        self._source_name = source_name

    @property
    def id(self):
        return self._id

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def descript(self):
        return self._descript

    @property
    def source_type(self):
        return self._source_type

    @property
    def source_name(self):
        return self._source_name
