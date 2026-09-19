from knotrack import Database
from knotrack import ScanDoc
from knotrack import search_documents
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

def test_search_documents_with_results(tmp_path, db):
    # Create and insert multiple scan documents
    scan_doc1 = make_scan_doc(tmp_path, title="First Document", content="This is the first test document.")
    scan_doc2 = replace(scan_doc1, title="Second Document", content="This is the second test document.", path=tmp_path / "second_scan.md")
    scan_doc3 = replace(scan_doc1, title="Third Document", content="This is the third test document.", path=tmp_path / "third_scan.md")

    db.insert_scan_doc(scan_doc1)
    db.insert_scan_doc(scan_doc2)
    db.insert_scan_doc(scan_doc3)

    # Search for documents containing the word "first"
    results = search_documents("first", db)
    assert len(results) == 1
    assert results[0] == scan_doc1

    # Search for documents containing the word "document"
    results = search_documents("document", db)
    assert len(results) == 3

def test_search_documents_limit(tmp_path, db):
    # Insert multiple scan documents
    for i in range(30):
        scan_doc = make_scan_doc(tmp_path, title=f"Title {i}", content=f"Content {i}", doc_name=f"scan_{i}.md")
        db.insert_scan_doc(scan_doc)

    # Search for scan documents with a common term
    results = search_documents("Title", db, limit=20)
    assert len(results) == 20  # Ensure all inserted documents are returned
    for i, result in enumerate(results):
        assert result.title == f"Title {i}"
        assert result.content == f"Content {i}"

def test_search_documents_no_results(tmp_path, db):
    results = search_documents("nonexistent", db)
    assert len(results) == 0