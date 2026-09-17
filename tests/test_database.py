from knotrack import Database
from knotrack import ScanDoc
import pytest
import sqlite3

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

    db.close()

def test_insert_and_check_scan_doc(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))

    # Create a new scan document
    scan_doc = ScanDoc(
        title="Test Scan",
        content="This is a test scan",
        content_hash="abc123",
        size=123,
        path=tmp_path / "test_scan.md"
    )

    # Insert the scan document into the database
    db.insert_scan_doc(scan_doc)
    checked_doc = db.get_scan_doc(str(scan_doc.path))
    assert checked_doc is not None
    assert checked_doc.title == scan_doc.title
    assert checked_doc.content == scan_doc.content
    assert checked_doc.content_hash == scan_doc.content_hash
    assert checked_doc.size == scan_doc.size
    assert checked_doc.path == scan_doc.path

    db.close()

def test_check_nonexistent_scan_doc(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))

    # Check for a scan document that doesn't exist
    checked_doc = db.get_scan_doc(str(tmp_path / "nonexistent.md"))
    assert checked_doc is None

    db.close()

def test_path_unique(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))

    scan_doc = ScanDoc(
            title="Test Scan",
            content="This is a test scan",
            content_hash="abc123",
            size=123,
            path=tmp_path / "test_scan.md"
        )
    db.insert_scan_doc(scan_doc)
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_scan_doc(scan_doc)
        # Attempt to insert the same document again

    db.close()

def test_database_consistent_data(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    scan_doc = ScanDoc(
            title="Test Scan",
            content="This is a test scan",
            content_hash="abc123",
            size=123,
            path=tmp_path / "test_scan.md"
        )
    db.insert_scan_doc(scan_doc)
    db.close()
    db = Database(str(db_path))
    checked_doc = db.get_scan_doc(str(scan_doc.path))
    assert checked_doc == scan_doc  # Ensure that the data is consistent after reopening the database

    db.close()

def test_update_scan_doc(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))

    # Create and insert a new scan document
    scan_doc = ScanDoc(
        title="Test Scan",
        content="This is a test scan",
        content_hash="abc123",
        size=123,
        path=tmp_path / "test_scan.md"
    )
    db.insert_scan_doc(scan_doc)

    # Update the scan document
    updated_scan_doc = ScanDoc(
        title="Updated Test Scan",
        content="This is an updated test scan",
        content_hash="def456",
        size=456,
        path=tmp_path / "test_scan.md"
    )
    db.update_scan_doc(updated_scan_doc)

    # Retrieve the updated scan document and check its values
    checked_doc = db.get_scan_doc(str(updated_scan_doc.path))
    assert checked_doc is not None
    assert checked_doc.title == updated_scan_doc.title
    assert checked_doc.content == updated_scan_doc.content
    assert checked_doc.content_hash == updated_scan_doc.content_hash
    assert checked_doc.size == updated_scan_doc.size
    assert checked_doc.path == updated_scan_doc.path

    db.close()