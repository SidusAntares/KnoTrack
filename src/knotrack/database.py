import sqlite3
from .model import ScanDoc
from pathlib import Path
class Database:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

        if not self.conn.execute('''SELECT 1 FROM sqlite_master
            WHERE type = 'table'
            AND name = 'documents_fts';
            ''').fetchone():
            self.create_fts_table()

        self.create_fts_table_triggers()

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                size INTEGER NOT NULL,
                path TEXT NOT NULL UNIQUE
            );
        ''')
        self.conn.commit()

    def create_fts_table(self):
        self.conn.execute('''
            CREATE VIRTUAL TABLE documents_fts USING
                fts5(title, content, content=documents, content_rowid='id');
        ''')
        self.conn.execute('''
            INSERT INTO documents_fts(documents_fts) VALUES('rebuild');
        ''')
        self.conn.commit()

    def create_fts_table_triggers(self):
        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, title, content)
                    VALUES (new.id, new.title, new.content);
            END;
        ''')
        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, rowid, title, content)
                    VALUES('delete', old.id, old.title, old.content);
            END;
        ''')
        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, rowid, title, content)
                    VALUES('delete', old.id, old.title, old.content);
                INSERT INTO documents_fts(rowid, title, content)
                    VALUES (new.id, new.title, new.content);
            END
        ''')
        self.conn.commit()

    def insert_scan_doc(self, scan_doc: ScanDoc):
        self.conn.execute('''
            INSERT INTO documents (title, content, content_hash, size, path)
            VALUES (?, ?, ?, ?, ?)
        ''', (scan_doc.title, scan_doc.content, scan_doc.content_hash, scan_doc.size, str(scan_doc.path)))
        self.conn.commit()

    def get_scan_doc(self,path: str):
        scan_doc = self.conn.execute('''
        SELECT title, content, content_hash, size, path FROM documents WHERE path = ?
        ''',(path,)).fetchone()
        if scan_doc:
            return ScanDoc(
                title=scan_doc[0],
                content=scan_doc[1],
                content_hash=scan_doc[2],
                size=scan_doc[3],
                path=Path(scan_doc[4])
            )
        return None

    def update_scan_doc(self, scan_doc: ScanDoc):
        self.conn.execute('''
            UPDATE documents
            SET title = ?, content = ?, content_hash = ?, size = ?
            WHERE path = ?
        ''', (scan_doc.title, scan_doc.content, scan_doc.content_hash, scan_doc.size, str(scan_doc.path)))
        self.conn.commit()

    def search_scan_docs(self, query: str):
        cursor = self.conn.execute('''
            SELECT d.title, d.content, d.content_hash, d.size, d.path FROM documents AS d JOIN documents_fts(?) ON d.id = documents_fts.rowid
            ORDER BY rank
        ''', (query,))
        results = []
        for row in cursor:
            results.append(ScanDoc(
                title=row[0],
                content=row[1],
                content_hash=row[2],
                size=row[3],
                path=Path(row[4])
            ))
        return results

    def close(self):
        self.conn.close()