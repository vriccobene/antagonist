# import uuid
# import psycopg2, psycopg2.extras
# from config import env
# from domain import symptom

# import logging
# logger = logging.getLogger(__name__)

# # Enable Psycopg2 to work with UUIDs
# psycopg2.extras.register_uuid()


# class SymptomRepository:

#     def save_to_database(self, symtpom_obj):
#         """
#         Save the symptom to the database and return the id of the saved symptom
#         """
#         conn = psycopg2.connect(
#             database=env.POSTGRESQL_DB_NAME, 
#             user=env.POSTGRESQL_DB_USER, 
#             password=env.POSTGRESQL_DB_PASSWORD, 
#             host=env.POSTGRESQL_DB_HOST, 
#             port=env.POSTGRESQL_DB_PORT)
#         cursor = conn.cursor()
#         symptom_id = self.persist(cursor, symtpom_obj)
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return symptom_id
    
#     def persist(self, cursor, symtpom:symptom.Symptom):
#         logger.debug(f"Persisting symptom {symtpom}")
#         self.store_symptom(cursor, symtpom)
#         symptom_id = cursor.fetchone()[0]
#         tags = symtpom.tags
#         self.store_tags(cursor, symptom_id, tags)
#         logger.debug(f"Persisted symptom with id {symptom_id}")
#         return symptom_id

#     def store_symptom(self, cursor, symptom:symptom.Symptom):
#         logger.debug(f"Storing symptom {symptom}")
#         cols = SymptomRepository._format_for_sql(str(symptom.get_field_keys()))
#         values = symptom.get_field_values()
#         cursor.execute(
#             "INSERT INTO symptom " \
#             f"{cols} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
#             "RETURNING id", tuple(values)
#         )
#         logger.info("Stored symptom in the database")

#     def store_tags(self, cursor, symptom_id:uuid.uuid4, tags:dict):
#         """
#         Store the tags of the symptom in the database
#         """
#         logger.debug(f"Storing tags for symptom {symptom_id}")
#         for tag_key, tag_value in tags.items():
#             cursor.execute("""
#                 INSERT INTO tag (symptom_id, tag_key, tag_value)
#                 VALUES (%s, %s, %s)
#             """, (symptom_id, tag_key, tag_value))
#         logger.info(f"Stored tags for symptom {symptom_id}")

#     @staticmethod
#     def _format_for_sql(column_names):
#         res = column_names.replace("[", "(").replace("]", ")").replace("'", "").replace("-", "_")
#         res = res.replace("description", "descript")
#         return res
    