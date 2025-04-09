# import psycopg2
# from config import env
# from antagonist.domain.network_anomaly import NetworkAnomaly


# class IncidentRepository:
#     def __init__(self):
#         self.conn = psycopg2.connect(
#             dbname=env.POSTGRESQL_DB_NAME,
#             user=env.POSTGRESQL_DB_USER,
#             password=env.POSTGRESQL_DB_PASSWORD,
#             host=env.POSTGRESQL_DB_HOST,
#             port=env.POSTGRESQL_DB_PORT
#         )
#         self.cur = self.conn.cursor()
    
#     def add_incident(self, incident:NetworkAnomaly):
#         res = ""
#         self.cur.execute('''
#             SELECT * FROM incidents WHERE tag = %s
#         ''', (incident.tag,))
#         existing_incident = self.cur.fetchone()
#         if existing_incident:
#             self.cur.execute('''
#                 UPDATE incidents SET start_time = %s, stop_time = %s, name = %s, description = %s WHERE tag = %s
#             ''', (incident.start_time, incident.stop_time, incident.name, incident.description, incident.tag))
#             res = "Incident updated" 
#         else:
#             self.cur.execute('''
#                 INSERT INTO incidents (start_time, stop_time, name, description, tag)
#                 VALUES (%s, %s, %s, %s, %s)
#             ''', (incident.start_time, incident.stop_time, incident.name, incident.description, incident.tag))
#             res = "Incident added"
#         self.conn.commit()
#         return res

#     def get_incidents(self):
#         self.cur.execute('SELECT * FROM incidents')
#         return self.cur.fetchall()

#     def __del__(self):
#         self.cur.close()
#         self.conn.close()
