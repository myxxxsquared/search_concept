
import dbconf

sql = 'INSERT INTO `search_concept` (concept_name) VALUES (?)'

lines = [[line.strip()] for line in open('names.txt', encoding='utf8') if line.strip()]

conn = dbconf.getconn()
cur = conn.cursor()
cur.executemany(sql, lines)
conn.commit()
