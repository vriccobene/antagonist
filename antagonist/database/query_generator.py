import pydantic
from datetime import datetime

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BasicEntity(pydantic.BaseModel):

    def __init__(self, **data):
        super().__init__(**data)
        self._non_sql_fields = {}

    def non_sql_field_names(self):
        res = list(self._non_sql_fields.keys()) 
        res += ['_non_sql_fields']
        return res
    
    def non_sql_field_dict(self):
        return self._non_sql_fields


class Symptom(BasicEntity):
    id: str | None
    network_anomaly_id: str | None
    start_time: str | None
    end_time: str | None
    concern_score: float | None
    confidence_score: float | None
    annotator_name: str | None
    annotator_type: str | None
    tags: dict | None

    def __init__(self, **data):
        super().__init__(**data)
        self._non_sql_fields = {
            'network_anomaly_id': {
                "inner_field": "id", 
                "external_table": "network_anomaly_contains_symptom",
                "external_field": "symptom_id"
            },
            'tags': {
                "inner_field": "id", 
                "external_table": "tag",
                "external_field": "symptom_id"
            },
            'annotator_name': None,
            'annotator_type': None,
            'start_time': None,
            'end_time': None,
            'confidence_score': None,
            'concern_score': None
        }

    def get_all_fields(self, tags=False):
        field_names = ['symptom.id', 'symptom.event_id', 'symptom.start_time', 
                   'symptom.end_time', 'symptom.descript', 
                   'symptom.confidence_score', 'symptom.concern_score', 
                   'symptom.source_name', 'symptom.source_type']
        res = str(field_names)
        res = res.replace('[', '').replace(']', '').replace("'", '')
        return res
    
    def add_specific_conditions(self, conditions, values):
        if self.start_time != None and self.end_time != None:
            conditions += " ((symptom.start_time >= %s AND symptom.start_time <= %s) OR " \
                          "(symptom.end_time >= %s AND symptom.end_time <= %s) OR " \
                          "(symptom.start_time <= %s AND symptom.end_time >= %s))    "
            values += (self.start_time, self.end_time, 
                       self.start_time, self.end_time, 
                       self.start_time, self.end_time)
        if self.network_anomaly_id:
            conditions += " network_anomaly_contains_symptom.network_anomaly_id = %s AND "
            values += (self.network_anomaly_id,)
        if self.tags:
            for tag in self.tags:
                conditions += " tag.name = %s AND tag.value = %s AND "
                values += (tag['name'], tag['value'])
        if self.annotator_name:
            conditions += " symptom.source_name = %s AND "
            values += (self.annotator_name,)
        if self.annotator_type: 
            conditions += " symptom.source_type = %s AND "
            values += (self.annotator_type,)
        if self.confidence_score:
            conditions += " symptom.confidence_score >= %s AND "
            values += (self.confidence_score,)
        if self.concern_score:
            conditions += " symptom.concern_score >= %s AND "
            values += (self.concern_score,)
        return conditions, values
    

class QueryGenerator:

    @staticmethod
    def generate_query(entity_type, parameters):
        entity = None
        if entity_type == "symptom":
            entity = Symptom(**parameters)
        else:
            raise ValueError(f"Entity type {entity_type} not supported")

        fields = str(list(
            [k for k in entity.__class__.model_fields.keys() 
             if k not in entity.non_sql_field_names()])). \
            replace('[', '').replace(']', '').replace("'", '')
        logger.info(f"Fields: {fields}")

        query = f"SELECT DISTINCT {entity.get_all_fields()} FROM {entity_type}"
        query = QueryGenerator.add_joins(parameters, entity, entity_type, query)
        query, values = QueryGenerator.add_conditions(entity, query, ())

        logger.info(f"Query: {query}")
        logger.info(f"Values: {values}")

        return query, values

    @staticmethod
    def add_joins(parameters, entity, entity_type, query):
        for parameter in parameters:
            if parameter not in entity.non_sql_field_names():
                continue
            if entity.non_sql_field_dict().get(parameter) is None:
                continue
            logger.info(f"Parameter: {parameter}")
            inner_field = entity.non_sql_field_dict()[parameter]['inner_field']
            external_table = entity.non_sql_field_dict()[parameter]['external_table']
            external_field = entity.non_sql_field_dict()[parameter]['external_field']
            query += f" INNER JOIN {external_table} ON {entity_type}.{inner_field} = {external_table}.{external_field}"
        return query

    @staticmethod
    def add_conditions(entity, query, values):
        conditions = ' WHERE'
        values = ()
        for field_name, field_value in entity.__dict__.items():
            if not field_value or field_name == '_non_sql_fields':
                continue
            if field_name in entity.non_sql_field_names():
                if entity.non_sql_field_dict()[field_name] is not None:
                    field_name = f"{entity.non_sql_field_dict()[field_name]['external_table']}." \
                                    f"{entity.non_sql_field_dict()[field_name]['external_field']}"
            else:
                logger.info(f'field name: {field_name}')
                conditions, values = QueryGenerator._add_condition(
                    conditions, values, field_name, field_value)
        
        conditions, values = entity.add_specific_conditions(conditions, values)
        if conditions != ' WHERE':
            # Remove the last 'AND'
            conditions = conditions[:-4]  
            query += conditions
        
        return query, values

    @staticmethod
    def _add_condition(conditions, values, field_name, field_value):
        conditions += f" {field_name} = %s AND"
        values += (field_value,)
        return conditions, values
