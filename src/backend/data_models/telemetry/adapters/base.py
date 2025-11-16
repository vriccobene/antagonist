from abc import ABC, abstractmethod
from typing import Dict, Any


class DataSourceAdapter(ABC):

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    @abstractmethod
    def query_metric(
            self,
            metric_mapping: Dict[str, Any],
            entity_fields: Dict[str, Any]) -> dict:
        pass
