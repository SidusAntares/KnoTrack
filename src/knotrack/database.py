import sqlite3
from .scanner import scan_doc
from .model import ScanDoc

class Database:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DOCUMENTS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                size INTEGER NOT NULL,
                path TEXT NOT NULL UNIQUE
            )
        ''')
        self.conn.commit()

    def insert_scan_doc(self, scan_doc: ScanDoc):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO DOCUMENTS (title, content, content_hash, size, path)
            VALUES (?, ?, ?, ?, ?)
        ''', (scan_doc.title, scan_doc.content, scan_doc.content_hash, scan_doc.size, str(scan_doc.path)))
        self.conn.commit()

    def check_scan_doc(self,path: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM DOCUMENTS WHERE path = ?
        ''',(path,))
        scan_doc = cursor.fetchall()
        if scan_doc:
            return ScanDoc(*scan_doc[0][1:])
        return None

    def close(self):
        self.conn.close()