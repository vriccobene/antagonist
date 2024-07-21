import uuid
import psycopg2, psycopg2.extras
from database import query_generator
from domain import network_anomaly, symptom_to_network_anomaly, annotator
from config import env
from domain import symptom
from database import database_base

import logging
logger = logging.getLogger(__name__)

# Enable Psycopg2 to work with UUIDs
psycopg2.extras.register_uuid()

class PostgresqlDatabase(database_base.DatabaseBase):
    """
    A class representing a PostgreSQL database.

    Attributes:
    - host (str): The host of the PostgreSQL database.
    - port (int): The port number of the PostgreSQL database.
    - database (str): The name of the PostgreSQL database.
    - user (str): The username for connecting to the PostgreSQL database.
    - password (str): The password for connecting to the PostgreSQL database.
    - connection (psycopg2.extensions.connection): The connection object for the PostgreSQL database.
    """

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Initializes a new instance of the PostgresqlDatabase class.

        Parameters:
        - host (str): The host of the PostgreSQL database.
        - port (int): The port number of the PostgreSQL database.
        - database (str): The name of the PostgreSQL database.
        - user (str): The username for connecting to the PostgreSQL database.
        - password (str): The password for connecting to the PostgreSQL database.
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """
        Connects to the PostgreSQL database.
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info("Connected to PostgreSQL!")
        except (Exception, psycopg2.Error) as error:
            logger.error("Error while connecting to PostgreSQL:", error)

    def disconnect(self):
        """
        Disconnects from the PostgreSQL database.
        """
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from PostgreSQL!")

    def store_network_anomaly(self, network_anomaly_object:network_anomaly.NetworkAnomaly):
        """
        Stores an netowrk anomaly in the PostgreSQL database.

        Parameters:
        - network_anomaly_object (network_anomaly.NetworkAnomaly): The network anomaly object to be stored.
        """
        try:
            cursor = self.connection.cursor()
            annotator = network_anomaly_object.annotator
            annotator_id = self._store_annotator(cursor, annotator)
            self._store_network_anomaly(cursor, network_anomaly_object, annotator_id)
            network_anomaly_id = cursor.fetchone()[0]
            self.connection.commit()
            return network_anomaly_id
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while storing network anomaly:", error)
            return None
            
    def get_network_anomaly(self, network_anomaly_id:uuid.uuid4=None):
        """
        Retrieves an network anomaly from the PostgreSQL database.

        Parameters:
        - network_anomaly_id (uuid.uuid4): The ID of the network anomaly to be retrieved.

        Returns:
        - network_anomaly_object (tuple): The retrieved network anomaly as a tuple.
        """

        # TODO - move data model related stuff in the entity definition
        def _convert_to_obj(network_anomaly_val):
            annotator = self._get_annotator(network_anomaly_val[2])
            res = network_anomaly.NetworkAnomaly({
                "description": network_anomaly_val[1], 
                "annotator": dict(annotator),
                "version": network_anomaly_val[3], 
                "state": network_anomaly_val[4]
            })
            res.id = network_anomaly_val[0]
            logger.info(f"RES: {dict(res)}")
            return res

        try:
            cursor = self.connection.cursor()
            if not network_anomaly_id:
                cursor.execute("SELECT * FROM network_anomaly")
                network_anomaly_list = cursor.fetchall()
                logger.debug(f"Retrieved network anomalies: {network_anomaly_list}")
                logger.info("Network Anomalies retrieved successfully!")
                return [_convert_to_obj(network_anomaly_val) for network_anomaly_val in network_anomaly_list] or None
            else:
                query = "SELECT * FROM network_anomaly WHERE id = %s"
                values = (network_anomaly_id,)
                logger.info(f"Query: {query}, values: {values}")
                cursor.execute(query, values)
                network_anomaly_val = cursor.fetchone()
                network_anomaly_obj = _convert_to_obj(network_anomaly_val)
                network_anomaly_obj.id = network_anomaly_val[0]
                logger.debug(f"Retrieved network anomaly: {network_anomaly_obj}")
                logger.info("Network anomaly retrieved successfully!")
                return network_anomaly_obj
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while retrieving network anomaly:", error)

    def store_symptom(self, symptom:symptom.Symptom):
        """
        Stores a symptom in the PostgreSQL database.

        Parameters:
        - symptom (symptom.Symptom): The symptom object to be stored.
        """
        try:
            cursor = self.connection.cursor()
            self._store_symptom(cursor, symptom)
            symptom_id = cursor.fetchone()[0]
            tags = symptom.tags
            self._store_tags(cursor, symptom_id, tags)
            self.connection.commit()
            return symptom_id
        except (Exception, psycopg2.Error) as error:
            logger.error("Error while storing symptom:", error)
            return None
    
    def add_tag_to_symptom(self, symptom_id, tag_key, tag_value):
        try:
            cursor = self.connection.cursor()
            self._store_tags(cursor, symptom_id, {tag_key: tag_value})
            self.connection.commit()
        except (Exception, psycopg2.Error) as error:
            logger.info(f"Got an exception here on this tag: {tag_key} = {tag_value}")
            logger.error("Error while adding new tag:", error)
            return None

    def store_symptom_network_anomaly_relation(
            self, symptom_to_network_anomaly:symptom_to_network_anomaly.SymptomToNetworkAnomaly):
        """
        Stores the relation between a symptom and an network anomaly in the PostgreSQL database.

        Parameters:
        - symptom_id (uuid.uuid4): The ID of the symptom.
        - network_anomaly_id (uuid.uuid4): The ID of the network anomaly.
        """
        try:
            cols = PostgresqlDatabase._format_for_sql(str(symptom_to_network_anomaly.get_field_keys()))
            values = symptom_to_network_anomaly.get_field_values()
            cursor = self.connection.cursor()
            cursor.execute(
                f"INSERT INTO network_anomaly_contains_symptom {cols} " \
                "VALUES (%s, %s)", tuple(values)
            )
            self.connection.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while storing symptom - network_anomaly relation:", error)
            return False

    def get_symptom(
            self, 
            symptom_id:uuid.uuid4=None, 
            network_anomaly_id:uuid.uuid4=None, 
            start_time:str=None, 
            end_time:str=None,
            min_confidence_score:float=0.0,
            min_concern_score:float=0.0,
            annotator_name:str=None,
            annotator_type:str=None, 
            tags:dict=None):
        """
        Retrieves a symptom from the PostgreSQL database.

        Parameters:
        - symptom_id (uuid.uuid4): The ID of the symptom to be retrieved.

        Returns:
        - symptom (tuple): The retrieved symptom as a tuple.
        """

        # TODO - move data model related stuff in the entity definition
        def _convert_to_obj(symptom_val):
            # TODO: Add checks to the tags
            res = symptom.Symptom({
                "event-id": str(symptom_val[1]),
                "start-time": str(symptom_val[2]).replace(' ', 'T'), 
                "end-time": str(symptom_val[3]).replace(' ', 'T'), 
                "description": symptom_val[4], 
                "confidence-score": symptom_val[5], 
                "concern-score": symptom_val[6], 
                "annotator": {
                    "name": symptom_val[7],
                    "annotator_type": symptom_val[8]
                },
                "tags": self._get_tags(symptom_val[0])
            })
            res.id = symptom_val[0]
            return res

        input_params = {
            'id': symptom_id, 
            'network_anomaly_id': network_anomaly_id, 
            'start_time': str(start_time) if start_time else None, 
            'end_time': str(end_time) if end_time else None, 
            'confidence_score': min_confidence_score, 
            'concern_score': min_concern_score, 
            'annotator_name': annotator_name, 
            'annotator_type': annotator_type, 
            'tags': tags
        }

        logger.info(f"Input Parameters: {input_params}")
        query, values = query_generator.QueryGenerator.generate_query("symptom", input_params)

        try:
            cursor = self.connection.cursor()
            logger.info("Getting ready for the query")
            if start_time and end_time:
                logger.info("Option 1") 
                cursor.execute(query, values)
                symptom_list = cursor.fetchall()
                logger.debug(f"Retrieved symptoms: {symptom_list}")
                logger.info("Symptoms retrieved successfully!")
                return [_convert_to_obj(symptom_val) for symptom_val in symptom_list] or []
            if not symptom_id and not network_anomaly_id:
                logger.info("Option 2")
                cursor.execute(query, values)
                symptom_list = cursor.fetchall()
                logger.debug(f"Retrieved symptoms: {symptom_list}")
                logger.info("Symptoms retrieved successfully!")
                return [_convert_to_obj(symptom_val) for symptom_val in symptom_list] or []
            elif not network_anomaly_id:
                logger.info("Option 3")
                cursor.execute(query, values)
                symptom_val = cursor.fetchone()
                if symptom_val is None:
                    logger.error(f"Symptom with ID {symptom_id} not found")
                    return list()
                logger.info(f"Symptom retrieved successfully: {symptom_val}")
                symptom_obj = _convert_to_obj(symptom_val)
                symptom_obj.id = symptom_val[0]
                logger.debug(f"Retrieved symptom: {symptom_obj}")
                logger.info("Symptom retrieved successfully!")
                return symptom_obj
            else:
                logger.info("Option 4")
                cursor.execute(query, values)
                symptom_list = cursor.fetchall()
                logger.info("Symptoms retrieved successfully!")
                return [_convert_to_obj(symptom_val) for symptom_val in symptom_list] or []

        except (Exception, psycopg2.Error) as error:
            logger.error("Error while retrieving symptom:", error)

    def _store_symptom(self, cursor, symptom:symptom.Symptom):
        """
        Stores all the simple attributes of a symptom in the database.

        Args:
            cursor: The database cursor.
            symptom (symptom.Symptom): The symptom object to store.

        Returns:
            int: The ID of the stored symptom.
        """
        logger.debug(f"Storing symptom {symptom}")
        cols = PostgresqlDatabase._format_for_sql(str(symptom.get_field_keys()))
        values = symptom.get_field_values()
        cursor.execute(
            "INSERT INTO symptom " \
            f"{cols} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" \
            "RETURNING id", tuple(values)
        )
        logger.info("Stored symptom in the database")

    def _store_tags(self, cursor, symptom_id:uuid.uuid4, tags:dict):
            """
            Store tags associated with a symptom in the database.

            Args:
                cursor: The database cursor.
                symptom_id (uuid.uuid4): The ID of the symptom.
                tags (dict): A dictionary containing the tags to be stored.

            Returns:
                None
            """
            for tag_key, tag_value in tags.items():
                cursor.execute("""
                    INSERT INTO tag (symptom_id, tag_key, tag_value)
                    VALUES (%s, %s, %s)
                """, (symptom_id, tag_key, tag_value))

    @staticmethod
    def _format_for_sql(column_names):
        res = column_names.replace("[", "(").replace("]", ")").replace("'", "").replace("-", "_")
        res = res.replace("description", "descript")
        return res

    def _store_annotator(self, cursor, annotator:annotator.Annotator):
        logger.debug(f"Storing annotator {annotator}")
        cols = PostgresqlDatabase._format_for_sql(str(annotator.get_field_keys()))
        values = annotator.get_field_values()
        try:
            cursor.execute(
                "INSERT INTO annotator " \
                f"{cols} VALUES (%s, %s)" \
                "RETURNING id", tuple(values)
            )
        except psycopg2.errors.UniqueViolation as e:
            self.connection.rollback()
            cursor.execute(
                "SELECT id FROM annotator WHERE name = %s AND annotator_type = %s", (annotator.name, annotator.annotator_type)
            )
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while storing annotator:", error)
            
        logger.debug("Stored annotator in the database")
        return cursor.fetchone()[0]

    def _store_network_anomaly(self, cursor, network_anomaly, annotator_id):
        logger.debug(f"Storing network anomaly {network_anomaly}")
        cols = self._get_network_anomaly_columns(network_anomaly)
        cols.append("annotator_id")
        cols = PostgresqlDatabase._format_for_sql(str(cols))
        values = self._get_network_anomaly_values(network_anomaly)
        values.append(annotator_id)
        cursor.execute(
            "INSERT INTO network_anomaly " \
            f"{cols} VALUES (%s, %s, %s, %s)" \
            "RETURNING id", tuple(values)
        )
        logger.debug("Stored network anomaly in the database")

    @staticmethod
    def _get_network_anomaly_columns(network_anomaly):
        cols = network_anomaly.get_field_keys()
        cols.remove("annotator")
        return cols
    
    @staticmethod
    def _get_network_anomaly_values(network_anomaly):
        values = network_anomaly.get_field_values()
        values.remove(network_anomaly.annotator)
        return values

    def _get_annotator(self, annotator_id:uuid.uuid4):
        """
        Retrieves an annotator from the PostgreSQL database.

        Parameters:
        - annotator_id (uuid.uuid4): The ID of the annotator to be retrieved.

        Returns:
        - annotator (tuple): The retrieved annotator as a tuple.
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM annotator WHERE id = %s"
            values = (annotator_id,)
            cursor.execute(query, values)
            annotator_sql = cursor.fetchone()
            logger.info("Annotator retrieved successfully!")
            res =  { 
                "name": annotator_sql[1], 
                "annotator_type": annotator_sql[2], 
            }
            return res  
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while retrieving annotator:", error)

    def _get_tags(self, symptom_id: uuid.UUID):
        """
        Retrieves the tags associated with a symptom from the PostgreSQL database.

        Parameters:
        - symptom_id (uuid.UUID): The ID of the symptom.

        Returns:
        - tags (dict): A dictionary containing the retrieved tags.
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT tag_key, tag_value FROM tag WHERE symptom_id = %s"
            values = (symptom_id,)
            cursor.execute(query, values)
            tags = {}
            for row in cursor.fetchall():
                tag_key, tag_value = row
                tags[tag_key] = tag_value
            return tags
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while retrieving tags:", error)
            return {}
