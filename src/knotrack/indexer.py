from .model import ScanDoc
from .database import Database
from typing import Iterable

def index_documents(scan_docs: Iterable[ScanDoc], db: Database):
    for new_scan_doc in scan_docs:
        old_scan_doc = db.get_scan_doc(str(new_scan_doc.path))
        if old_scan_doc is None:
            db.insert_scan_doc(new_scan_doc)
        elif old_scan_doc.content_hash != new_scan_doc.content_hash:
            db.update_scan_doc(new_scan_doc)
        else:
            # Document is unchanged, do nothing
            pass
