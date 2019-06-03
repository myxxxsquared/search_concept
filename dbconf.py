
# import mysql.connector

# DBHOST = 'localhost'
# DBUSER = 'search_concept'
# DBPASS = 'mysearch'
# DBNAME = 'search_concept'

# def getconn():
#     return mysql.connector.connect(
#         host=DBHOST,
#         user=DBUSER,
#         passwd=DBPASS,
#         database=DBNAME
#     )

SQL_CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS `search_concept` (
    `concept_id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `concept_name` TEXT,
    `concept_found` INTEGER,
    `concept_detail` TEXT
);
'''

import sqlite3

DBFILE = 'search_concept.db'
def getconn():
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    cursor.execute(SQL_CREATE_TABLE)
    conn.commit()
    return conn
