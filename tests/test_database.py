from knotrack import Database
from knotrack import ScanDoc

def test_initialize_database(tmp_path):
    # Test that the database initializes correctly
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))  # Use an in-memory database for testing
    assert db is not None

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
    checked_doc = db.check_scan_doc(str(scan_doc.path))
    assert checked_doc is not None
    assert checked_doc.title == scan_doc.title
    assert checked_doc.content == scan_doc.content
    assert checked_doc.content_hash == scan_doc.content_hash
    assert checked_doc.size == scan_doc.size
    assert checked_doc.path == str(scan_doc.path)

def test_check_nonexistent_scan_doc(tmp_path):
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))

    # Check for a scan document that doesn't exist
    checked_doc = db.check_scan_doc(str(tmp_path / "nonexistent.md"))
    assert checked_doc is None

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
    checked_doc1 = db.check_scan_doc(str(scan_doc.path))
    db.insert_scan_doc(scan_doc)  # Attempt to insert the same document again
    checked_doc2 = db.check_scan_doc(str(scan_doc.path))
    assert checked_doc1 == checked_doc2  # The second insert should be ignored, so both checks should return the same document


