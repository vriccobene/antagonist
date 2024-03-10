import uuid
import psycopg2, psycopg2.extras
from config import env
from domain import symptom, incident, symptom_to_incident
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

    def store_incident(self, incident_object:incident.Incident):
        """
        Stores an incident in the PostgreSQL database.

        Parameters:
        - incident_object (incident.Incident): The incident object to be stored.
        """
        try:
            cursor = self.connection.cursor()
            author = incident_object.author
            author_id = self._store_author(cursor, author)
            self._store_incident(cursor, incident_object, author_id)
            incident_id = cursor.fetchone()[0]
            self.connection.commit()
            return incident_id
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while storing incident:", error)
            return None
            
    def get_incident(self, incident_id:uuid.uuid4=None):
        """
        Retrieves an incident from the PostgreSQL database.

        Parameters:
        - incident_id (uuid.uuid4): The ID of the incident to be retrieved.

        Returns:
        - incident_object (tuple): The retrieved incident as a tuple.
        """

        # TODO - move data model related stuff in the entity definition
        def _convert_to_obj(incident_val):
            auth = self._get_author(incident_val[2])
            # auth['id'] = incident_val[2]
            res = incident.Incident({
                "description": incident_val[1], 
                "author": auth,
                "version": incident_val[3], 
                "state": incident_val[4]
            })
            res.id = incident_val[0]
            return res

        try:
            cursor = self.connection.cursor()
            if not incident_id:
                cursor.execute("SELECT * FROM incident")
                incident_list = cursor.fetchall()
                logger.debug(f"Retrieved incidents: {incident_list}")
                logger.info("Incidents retrieved successfully!")
                return [_convert_to_obj(incident_val) for incident_val in incident_list] or None
            else:
                query = "SELECT * FROM incident WHERE id = %s"
                values = (incident_id,)
                cursor.execute(query, values)
                incident_val = cursor.fetchone()
                incident_obj = _convert_to_obj(incident_val)
                incident_obj.id = incident_val[0]
                logger.debug(f"Retrieved incident: {incident_obj}")
                logger.info("Incident retrieved successfully!")
                return incident_obj
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while retrieving incident:", error)

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

    def store_symptom_incident_relation(
            self, symptom_to_incident:symptom_to_incident.SymptomToIncident):
        """
        Stores the relation between a symptom and an incident in the PostgreSQL database.

        Parameters:
        - symptom_id (uuid.uuid4): The ID of the symptom.
        - incident_id (uuid.uuid4): The ID of the incident.
        """
        try:
            cols = PostgresqlDatabase._format_for_sql(str(symptom_to_incident.get_field_keys()))
            values = symptom_to_incident.get_field_values()
            cursor = self.connection.cursor()
            cursor.execute(
                f"INSERT INTO incident_contains_symptom {cols} " \
                "VALUES (%s, %s)", tuple(values)
            )
            self.connection.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while storing symptom-incident relation:", error)
            return False

    # def get_symptom_to_incident(self, incident_id:uuid.uuid4):
    #     """
    #     Retrieves the relation between a symptom and an incident from the PostgreSQL database.

    #     Parameters:
    #     - incident_id (uuid.uuid4): The ID of the incident.

    #     Returns:
    #     - symptom_to_incident (tuple): The retrieved relation between a symptom and an incident as a tuple.
    #     """

    #     def _convert_to_object(val):
    #         return symptom_to_incident.SymptomToIncident({
    #             "incident-id": str(val[0]),
    #             "symptom-id": str(val[1])
    #         })
        
    #     if incident_id is None:
    #         return None

    #     try:
    #         cursor = self.connection.cursor()
    #         query = "SELECT incident_id, symptom_id FROM incident_contains_symptom WHERE incident_id = %s"
    #         values = (incident_id,)
    #         cursor.execute(query, values)
    #         symptom_to_incident_list = cursor.fetchall()
    #         logger.debug(f"Retrieved symptom-incident relations: {symptom_to_incident_list}")
    #         logger.info("Symptom-incident relations retrieved successfully!")
    #         return [_convert_to_object(entry) for entry in symptom_to_incident_list] or None
    #     except (Exception, psycopg2.Error) as error:
    #         self.connection.rollback()
    #         logger.error("Error while retrieving symptom-incident relation:", error)

    def get_symptom(
            self, symptom_id:uuid.uuid4=None, incident_id:uuid.uuid4=None, 
            start_time:str=None, end_time:str=None):
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
            tags = self._get_tags(symptom_val[0])
            res = symptom.Symptom({
                "event-id": str(symptom_val[1]),
                "start-time": str(symptom_val[2]).replace(' ', 'T'), 
                "end-time": str(symptom_val[3]).replace(' ', 'T'), 
                "description": symptom_val[4], 
                "confidence-score": symptom_val[5], 
                "concern-score": symptom_val[6], 
                "plane": symptom_val[7], 
                "reason": symptom_val[8],
                "action": symptom_val[9], 
                "cause": symptom_val[10], 
                "pattern": symptom_val[11], 
                "source-type": symptom_val[12], 
                "source-name": symptom_val[13],
                "tags": tags
            })
            res.id = symptom_val[0]
            return res

        try:
            cursor = self.connection.cursor()

            if start_time and end_time:
                # Retrieve all symptoms within a time range
                query = "SELECT " \
                        "id, event_id, start_time, end_time, descript, confidence_score, " \
                        "concern_score, plane, reason, action, cause, pattern, " \
                        "source_type, source_name " \
                        "FROM symptom " \
                        "WHERE (start_time >= %s AND start_time <= %s) OR " \
                              "(end_time >= %s AND end_time <= %s) OR " \
                              "(start_time <= %s AND end_time >= %s)"
                values = (start_time, end_time, start_time, end_time, end_time, start_time,)
                cursor.execute(query, values)
                symptom_list = cursor.fetchall()
                logger.debug(f"Retrieved symptoms: {symptom_list}")
                logger.info("Symptoms retrieved successfully!")
                return [_convert_to_obj(symptom_val) for symptom_val in symptom_list] or []
            if not symptom_id and not incident_id:
                cursor.execute(
                    "SELECT " \
                    "id, event_id, start_time, end_time, descript, confidence_score, " \
                    "concern_score, plane, reason, action, cause, pattern, source_type, source_name " \
                    "FROM symptom")
                symptom_list = cursor.fetchall()
                logger.debug(f"Retrieved symptoms: {symptom_list}")
                logger.info("Symptoms retrieved successfully!")
                return [_convert_to_obj(symptom_val) for symptom_val in symptom_list] or []
            elif not incident_id:
                query = "SELECT symptom.* " \
                    "id, event_id, start_time, end_time, descript, confidence_score, " \
                    "concern_score, plane, reason, action, cause, pattern, source_type, source_name " \
                    " FROM symptom WHERE id = %s"
                values = (symptom_id,)
                cursor.execute(query, values)
                symptom_val = cursor.fetchone()
                symptom_obj = _convert_to_obj(symptom_val)
                symptom_obj.id = symptom_val[0]
                logger.debug(f"Retrieved symptom: {symptom_obj}")
                logger.info("Symptom retrieved successfully!")
                return symptom_obj
            else:
                # Retrieve all symptoms associated with an incident
                query = "SELECT " \
                        "symptom.id, symptom.event_id, symptom.start_time, symptom.end_time, " \
                        "symptom.descript, symptom.confidence_score, symptom.concern_score, " \
                        "symptom.plane, symptom.reason, symptom.action, symptom.cause, " \
                        "symptom.pattern, symptom.source_type, symptom.source_name " \
                        "FROM symptom " \
                        "INNER JOIN incident_contains_symptom " \
                        "ON symptom.id=incident_contains_symptom.symptom_id " \
                        "WHERE incident_contains_symptom.incident_id = %s"
                values = (incident_id,)
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
        print(cols)
        print(values)
        cursor.execute(
            "INSERT INTO symptom " \
            f"{cols} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
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

    def _store_author(self, cursor, author):
        logger.debug(f"Storing author {author}")
        cols = PostgresqlDatabase._format_for_sql(str(author.get_field_keys()))
        values = author.get_field_values()
        try:
            cursor.execute(
                "INSERT INTO author " \
                f"{cols} VALUES (%s, %s, %s)" \
                "RETURNING id", tuple(values)
            )
        except psycopg2.errors.UniqueViolation as e:
            self.connection.rollback()
            cursor.execute(
                "SELECT id FROM author WHERE name = %s AND author_type = %s", (author.name, author.author_type)
            )
        logger.debug("Stored author in the database")
        return cursor.fetchone()[0]

    def _store_incident(self, cursor, incident, author_id):
        logger.debug(f"Storing incident {incident}")
        cols = self._get_incident_columns(incident)
        cols.append("author_id")
        cols = PostgresqlDatabase._format_for_sql(str(cols))
        values = self._get_incident_values(incident)
        values.append(author_id)
        cursor.execute(
            "INSERT INTO incident " \
            f"{cols} VALUES (%s, %s, %s, %s)" \
            "RETURNING id", tuple(values)
        )
        logger.debug("Stored incident in the database")

    @staticmethod
    def _get_incident_columns(incident):
        cols = incident.get_field_keys()
        cols.remove("author")
        return cols
    
    @staticmethod
    def _get_incident_values(incident):
        values = incident.get_field_values()
        values.remove(incident.author)
        return values

    def _get_author(self, author_id:uuid.uuid4):
        """
        Retrieves an author from the PostgreSQL database.

        Parameters:
        - author_id (uuid.uuid4): The ID of the author to be retrieved.

        Returns:
        - author (tuple): The retrieved author as a tuple.
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM author WHERE id = %s"
            values = (author_id,)
            cursor.execute(query, values)
            author_sql = cursor.fetchone()
            logger.info("Author retrieved successfully!")
            res =  { 
                "name": author_sql[1], 
                "author_type": author_sql[2], 
            }
            if author_sql[3]:
                res["version"] = author_sql[3]
            return res  
        except (Exception, psycopg2.Error) as error:
            self.connection.rollback()
            logger.error("Error while retrieving author:", error)

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
