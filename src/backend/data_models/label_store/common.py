from enum import StrEnum


class AnnotatorType(StrEnum):
    human = 'human'
    algorithm = 'algorithm'


class State(StrEnum):
    anomaly = 'anomaly'
    incident = 'incident'
    unknown = 'unknown'
    forecasted = 'forecasted'
    potential = 'potential'
    discarded = 'discarded'
    confirmed = 'confirmed'
    analyzed = 'analyzed'
    adjusted = 'adjusted'


class AnomalyPattern(StrEnum):
    drop = 'drop'
    spike = 'spike'
    trend = 'trend'
    mean_shift = 'mean_shift'
    seasonality_shift = 'seasonality_shift'
    other = 'other'
