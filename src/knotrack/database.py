import sqlite3
from .model import ScanDoc
from pathlib import Path
class Database:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS DOCUMENTS (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                size INTEGER NOT NULL,
                path TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()

    def insert_scan_doc(self, scan_doc: ScanDoc):
        self.conn.execute('''
            INSERT INTO DOCUMENTS (title, content, content_hash, size, path)
            VALUES (?, ?, ?, ?, ?)
        ''', (scan_doc.title, scan_doc.content, scan_doc.content_hash, scan_doc.size, str(scan_doc.path)))
        self.conn.commit()

    def get_scan_doc(self,path: str):
        scan_doc = self.conn.execute('''
        SELECT TITLE, CONTENT, CONTENT_HASH, SIZE, PATH FROM DOCUMENTS WHERE path = ?
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
            UPDATE DOCUMENTS
            SET title = ?, content = ?, content_hash = ?, size = ?
            WHERE path = ?
        ''', (scan_doc.title, scan_doc.content, scan_doc.content_hash, scan_doc.size, str(scan_doc.path)))
        self.conn.commit()

    def search_scan_docs(self, query: str):
        cursor = self.conn.execute('''
            SELECT TITLE, CONTENT, CONTENT_HASH, SIZE, PATH FROM DOCUMENTS
            WHERE title LIKE ? OR content LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
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