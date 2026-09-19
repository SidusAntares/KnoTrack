from knotrack import Database
from knotrack import ScanDoc
from dataclasses import replace
import pytest
import sqlite3

@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    yield database
    database.close()

def make_scan_doc(tmp_path,
                  title = 'Test Scan',
                  content = 'This is a test scan',
                  content_hash = 'abc123',
                  size = 123,
                  doc_name =  "test_scan.md"):
    return ScanDoc(
        title=title,
        content=content,
        content_hash=content_hash,
        size=size,
        path=tmp_path / doc_name
    )

def test_initialize_database(tmp_path):
    # Test that the database initializes correctly
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    assert db is not None
    # documents = db.conn.execute("select 1 from sqlite_master" \
    # "where type = 'table' and name = 'DOCUMENTS';").fetchone()
    documents = db.conn.execute('''
    SELECT 1 FROM sqlite_master
    WHERE type = 'table'
    AND name = 'DOCUMENTS';
''').fetchone()
    assert documents is not None

def test_insert_and_check_scan_doc(tmp_path, db):
    # Create a new scan document
    scan_doc = make_scan_doc(tmp_path)

    # Insert the scan document into the database
    db.insert_scan_doc(scan_doc)
    checked_doc = db.get_scan_doc(str(scan_doc.path))
    assert checked_doc is not None
    assert checked_doc == scan_doc

def test_check_nonexistent_scan_doc(tmp_path, db):
    # Check for a scan document that doesn't exist
    checked_doc = db.get_scan_doc(str(tmp_path / "nonexistent.md"))
    assert checked_doc is None

def test_path_unique(tmp_path, db):
    scan_doc = make_scan_doc(tmp_path)
    db.insert_scan_doc(scan_doc)
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_scan_doc(scan_doc)
        # Attempt to insert the same document again

def test_database_consistent_data(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    scan_doc = make_scan_doc(tmp_path)
    db.insert_scan_doc(scan_doc)
    db.close()  # Close the database to simulate reopening
    db = Database(str(db_path))
    checked_doc = db.get_scan_doc(str(scan_doc.path))
    assert checked_doc == scan_doc  # Ensure that the data is consistent after reopening the database

def test_update_scan_doc(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))

    # Create and insert a new scan document
    scan_doc = make_scan_doc(tmp_path)
    db.insert_scan_doc(scan_doc)

    # Update the scan document
    updated_scan_doc = replace(scan_doc,
        content="This is an updated test scan",
        content_hash="def456")
    db.update_scan_doc(updated_scan_doc)

    # Retrieve the updated scan document and check its values
    checked_doc = db.get_scan_doc(str(updated_scan_doc.path))
    assert checked_doc is not None
    assert checked_doc == updated_scan_doc

def test_search_scan_doc_by_title(tmp_path, db):
    # Create and insert a new scan document
    scan_doc = make_scan_doc(tmp_path, title="Unique Title")
    db.insert_scan_doc(scan_doc)

    # Search for the scan document by title
    results = db.search_scan_docs("Unique Title")
    assert len(results) == 1
    assert results[0] == scan_doc

def test_search_scan_doc_by_content(tmp_path, db):
    scan_doc = make_scan_doc(tmp_path, content="Unique Content")
    db.insert_scan_doc(scan_doc)
    results = db.search_scan_docs("Unique Content")
    assert len(results) == 1
    assert results[0] == scan_doc

def test_search_scan_docs_with_results(tmp_path, db):
    # Create and insert multiple scan documents
    scan_doc1 = make_scan_doc(tmp_path, title="First Document", content="This is the first test document.")
    scan_doc2 = replace(scan_doc1, title="Second Document", content="This is the second test document.",path=tmp_path / "second_scan.md")
    scan_doc3 = replace(scan_doc1, title="Third Document", content="This is the third test document.", path=tmp_path / "third_scan.md")

    db.insert_scan_doc(scan_doc1)
    db.insert_scan_doc(scan_doc2)
    db.insert_scan_doc(scan_doc3)

    # Search for documents containing the word "first"
    results = db.search_scan_docs("first")
    assert len(results) == 1
    assert results[0] == scan_doc1

    # Search for documents containing the word "document"
    results = db.search_scan_docs("document")
    assert len(results) == 3

def test_search_scan_doc_no_results(tmp_path, db):
    scan_doc = make_scan_doc(tmp_path)
    db.insert_scan_doc(scan_doc)
    results = db.search_scan_docs("Nonexistent Query")
    assert len(results) == 0


def test_search_scan_docs_with_special_query(tmp_path, db):
    # Insert a scan document with special characters in the title and content
    scan_doc = make_scan_doc(tmp_path, title="Special!@#$%'^&*()_+Title")
    db.insert_scan_doc(scan_doc)

    # Search for the scan document using a special character query
    results = db.search_scan_docs("@#$%'^&*()_+")
    assert len(results) == 1
    assert results[0] == scan_doc