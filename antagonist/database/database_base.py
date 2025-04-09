import abc
import uuid
from domain.network_anomaly import NetworkAnomaly
from domain.symptom import Symptom


class DatabaseBase:

    @abc.abstractmethod
    def connect(self):
        raise NotImplementedError
     
    @abc.abstractmethod
    def disconnect(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def store_network_anomaly(self, incident:NetworkAnomaly):
        raise NotImplementedError
    
    @abc.abstractmethod
    def retrieve_incident(self, incident_id:uuid.uuid4):
        raise NotImplementedError
    
    @abc.abstractmethod
    def store_symptom(self, symptom:Symptom):
        raise NotImplementedError
    
    @abc.abstractmethod
    def retrieve_symptom(self, symptom_id:uuid.uuid4):
        raise NotImplementedError
