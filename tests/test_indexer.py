from knotrack import index_documents
from knotrack import ScanDoc
from knotrack import Database
from dataclasses import replace
import pytest

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

def test_index_insert_scan_doc(tmp_path, db):
    scan_doc = make_scan_doc(tmp_path)
    assert db.get_scan_doc(str(scan_doc.path)) is None
    index_documents([scan_doc], db)
    get_scan_doc = db.get_scan_doc(str(scan_doc.path))
    assert get_scan_doc == scan_doc


def test_index_update_scan_doc(tmp_path, db):
    # Insert an initial scan document
    scan_doc = make_scan_doc(tmp_path)
    db.insert_scan_doc(scan_doc)

    # Create an updated scan document with the same path but different content
    updated_scan_doc = replace(scan_doc,
        content="This is an updated test scan",
        content_hash="def456")

    index_documents([updated_scan_doc], db)
    get_scan_doc = db.get_scan_doc(str(updated_scan_doc.path))
    assert get_scan_doc == updated_scan_doc


def test_index_skip_unchanged_scan_doc(tmp_path, db):
    # Insert an initial scan document
    scan_doc = make_scan_doc(tmp_path)
    db.insert_scan_doc(scan_doc)

    # Create an unchanged scan document with the same path and content
    unchanged_scan_doc = replace(scan_doc,
        content="This is an unchanged test scan",
        content_hash="abc123")  # Same content hash as the original
    index_documents([unchanged_scan_doc], db)
    get_scan_doc = db.get_scan_doc(str(unchanged_scan_doc.path))
    # Keep the same hash but change other fields deliberately.
    # This verifies that indexer treats content_hash as the change criterion
    # and does not update the stored document.
    assert get_scan_doc == scan_doc  # Ensure that the document remains unchanged
    assert get_scan_doc != unchanged_scan_doc



def test_index_multiple_scan_docs(tmp_path, db):
    scan_doc1 = make_scan_doc(tmp_path)
    unchanged_scan_doc = replace(scan_doc1,
        content="This is an unchanged test scan")
    scan_doc2 = make_scan_doc(tmp_path, title="Second Test Scan",
                              content="This is the second test scan",
                              content_hash="ghi789",
                              doc_name="second_test_scan.md")
    updated_scan_doc = replace(scan_doc2,
        title="Updated Test Scan",
        content="This is an updated test scan",
        content_hash="def456",
        size=456)
    scan_doc3 = make_scan_doc(tmp_path, title="Third Test Scan",
                                content="This is the third test scan",
                                content_hash="jkl012",
                                doc_name="third_test_scan.md")
    db.insert_scan_doc(scan_doc1)
    db.insert_scan_doc(scan_doc2)
    index_documents([unchanged_scan_doc, updated_scan_doc, scan_doc3], db)
    get_scan_doc1 = db.get_scan_doc(str(scan_doc1.path))
    assert get_scan_doc1 == scan_doc1  # Ensure that the document is indexed correctly
    assert get_scan_doc1 != unchanged_scan_doc  # Ensure that the document remains unchanged
    get_scan_doc2 = db.get_scan_doc(str(updated_scan_doc.path))
    assert get_scan_doc2 == updated_scan_doc  # Ensure that the document is indexed correctly
    get_scan_doc3 = db.get_scan_doc(str(scan_doc3.path))
    assert get_scan_doc3 == scan_doc3  # Ensure that the document is indexed correctly

