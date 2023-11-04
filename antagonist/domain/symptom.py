class Symptom:
    def __init__(
            self, id=None, event_id=None, start_time=None, end_time=None, 
            descript=None, confidence_score=None, concern_score=None, 
            plane=None, condition=None, action=None, cause=None, 
            pattern=None, source_type=None, source_name=None):
        self._id = id
        self._event_id = event_id
        self._start_time = start_time
        self._end_time = end_time
        self._descript = descript
        self._confidence_score = confidence_score
        self._concern_score = concern_score
        self._plane = plane
        self._condition = condition
        self._action = action
        self._cause = cause
        self._pattern = pattern
        self._source_type = source_type
        self._source_name = source_name

    @property
    def id(self):
        return self._id

    @property
    def event_id(self):
        return self._event_id

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        self._start_time = value

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        self._end_time = value

    @property
    def descript(self):
        return self._descript

    @descript.setter
    def descript(self, value):
        self._descript = value

    @property
    def confidence_score(self):
        return self._confidence_score

    @confidence_score.setter
    def confidence_score(self, value):
        self._confidence_score = value

    @property
    def concern_score(self):
        return self._concern_score

    @concern_score.setter
    def concern_score(self, value):
        self._concern_score = value

    @property
    def plane(self):
        return self._plane

    @plane.setter
    def plane(self, value):
        self._plane = value
    
    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self, value):
        self._condition = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value

    @property
    def cause(self):
        return self._cause

    @cause.setter
    def cause(self, value):
        self._cause = value

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        self._pattern = value

    @property
    def source_type(self):
        return self._source_type

    @source_type.setter
    def source_type(self, value):
        self._source_type = value

    @property
    def source_name(self):
        return self._source_name

    @source_name.setter
    def source_name(self, value):
        self._source_name = value
