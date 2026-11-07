import sqlite3,sys
from pathlib import Path
D=sqlite3.connect(Path(sys.argv[1])/'base_maestra.sqlite');D.execute('PRAGMA foreign_keys=ON');D.executescript('''
CREATE TABLE workbook_keys(id INTEGER PRIMARY KEY,workbook TEXT UNIQUE);
INSERT INTO workbook_keys(workbook) SELECT DISTINCT workbook FROM source_records ORDER BY workbook;
CREATE TABLE source_table_keys(id INTEGER PRIMARY KEY,table_name TEXT UNIQUE);
INSERT INTO source_table_keys(table_name) SELECT DISTINCT table_name FROM source_records ORDER BY table_name;
CREATE TABLE payload_keys(id INTEGER PRIMARY KEY,row_hash TEXT UNIQUE REFERENCES source_payloads(row_hash));
INSERT INTO payload_keys(row_hash) SELECT row_hash FROM source_payloads ORDER BY row_hash;
CREATE TABLE source_links(snapshot TEXT,workbook_id INTEGER REFERENCES workbook_keys(id),table_id INTEGER REFERENCES source_table_keys(id),payload_id INTEGER REFERENCES payload_keys(id),PRIMARY KEY(snapshot,workbook_id,table_id,payload_id)) WITHOUT ROWID;
INSERT INTO source_links SELECT s.snapshot,w.id,t.id,p.id FROM source_records s JOIN workbook_keys w USING(workbook) JOIN source_table_keys t USING(table_name) JOIN payload_keys p USING(row_hash);
DROP TABLE source_records;
CREATE VIEW source_records AS SELECT s.snapshot,w.workbook,t.table_name,p.row_hash FROM source_links s JOIN workbook_keys w ON w.id=s.workbook_id JOIN source_table_keys t ON t.id=s.table_id JOIN payload_keys p ON p.id=s.payload_id;
''');D.commit();D.execute('VACUUM');assert D.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not D.execute('PRAGMA foreign_key_check').fetchall();print(D.execute('select count(*) from source_records').fetchone());D.close()
