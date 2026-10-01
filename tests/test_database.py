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
    AND name = 'documents';
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


# ---------------------------------------------------------------------------
# FTS5 index tests (named test_fts5_<target>_<behaviour>)
#
# These tests describe the observable behaviour of the search index: they go
# through the Database API (plus the plain `documents` table) and never inspect
# the FTS table itself. Results are compared as sets, so no test depends on the
# order in which matches come back.
# ---------------------------------------------------------------------------

def build_database_without_fts5(db_path, tmp_path, docs=None):
    """Write a database file that holds `documents` rows but no FTS table.

    Mimics a file produced before FTS5 support existed, so tests can check that
    opening it with Database builds the index on demand.
    """
    if docs is None:
        docs = [("Legacy Title", "legacy content", "legacy.md")]

    conn = sqlite3.connect(str(db_path))
    conn.execute('''
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            size INTEGER NOT NULL,
            path TEXT NOT NULL UNIQUE
        );
    ''')
    for title, content, doc_name in docs:
        conn.execute('''
            INSERT INTO documents (title, content, content_hash, size, path)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, "legacyhash", len(content), str(tmp_path / doc_name)))
    conn.commit()
    conn.close()


def build_database_with_fts5_but_no_triggers(db_path):
    """Write a database file whose FTS table exists but whose sync triggers do not.

    Reproduces a file left behind by an initialization that committed the FTS table before
    its triggers were created, so a test can check the triggers are backfilled on open.
    """
    database = Database(str(db_path))
    # Drop the sync triggers by name: there is no API for "create the index without them"
    database.conn.executescript('''
        DROP TRIGGER documents_ai;
        DROP TRIGGER documents_ad;
        DROP TRIGGER documents_au;
    ''')
    database.conn.commit()
    database.close()


def paths_of(results):
    return {doc.path for doc in results}


def test_fts5_reopen_keeps_index_in_sync(tmp_path):
    """Reopening a database that already has an index must not lose or duplicate entries.

    Documents written before and after the reopen are both searchable exactly once, so this
    covers both the trigger setup and the "FTS table already exists" branch.
    """
    db_path = tmp_path / "test.db"
    first = make_scan_doc(tmp_path, content="reopentoken one", doc_name="first.md")

    db = Database(str(db_path))
    db.insert_scan_doc(first)
    db.close()

    db = Database(str(db_path))
    try:
        second = make_scan_doc(tmp_path, content="reopentoken two", doc_name="second.md")
        db.insert_scan_doc(second)

        results = db.search_scan_docs("reopentoken")
        assert len(results) == 2
        assert paths_of(results) == {first.path, second.path}
    finally:
        db.close()


def test_fts5_create_fts_table_rebuilds_existing_documents(tmp_path):
    """Opening a database that has documents but no FTS table builds the index on demand.

    Rows written before FTS support existed become searchable without being re-inserted,
    which only holds if the newly created table was rebuilt from the documents table.
    """
    db_path = tmp_path / "legacy.db"
    build_database_without_fts5(db_path, tmp_path)

    db = Database(str(db_path))
    try:
        assert paths_of(db.search_scan_docs("legacy")) == {tmp_path / "legacy.md"}
    finally:
        db.close()


def test_fts5_create_fts_table_installs_insert_trigger(tmp_path):
    """Creating the FTS table on demand also installs the sync triggers.

    The rebuild only covers historical rows, so this asserts that a document inserted after
    the reopen is searchable too, i.e. the insert trigger was created on this open.
    """
    db_path = tmp_path / "legacy.db"
    build_database_without_fts5(db_path, tmp_path)

    db = Database(str(db_path))
    try:
        doc = make_scan_doc(tmp_path, content="freshtoken", doc_name="fresh.md")
        db.insert_scan_doc(doc)

        assert paths_of(db.search_scan_docs("freshtoken")) == {doc.path}
    finally:
        db.close()


def test_fts5_open_backfills_missing_triggers(tmp_path):
    """Opening a database whose FTS table exists without its triggers restores them.

    Initialization only creates the FTS table when it is missing, so reaching this state
    means a file that already holds the table never runs that branch again: unless the sync
    triggers are created on open, documents inserted afterwards would never reach the index
    and would stay unsearchable. The inserted document being findable shows they were.
    """
    db_path = tmp_path / "notriggers.db"
    build_database_with_fts5_but_no_triggers(db_path)

    db = Database(str(db_path))
    try:
        doc = make_scan_doc(tmp_path, content="backfilltoken", doc_name="backfill.md")
        db.insert_scan_doc(doc)

        assert paths_of(db.search_scan_docs("backfilltoken")) == {doc.path}
    finally:
        db.close()


def test_fts5_update_trigger_replaces_index_entry(tmp_path, db):
    """Updating a document replaces its index entry rather than appending to it.

    After the update the old content no longer matches and the new content matches once:
    delete-only would lose the new content, while insert-only would keep matching the old
    content, since the external content table returns the updated row.
    """
    doc = make_scan_doc(tmp_path, title="Update Target", content="oldtoken")
    db.insert_scan_doc(doc)
    assert len(db.search_scan_docs("oldtoken")) == 1

    updated = replace(doc, content="newtoken", content_hash="def456")
    db.update_scan_doc(updated)

    assert db.search_scan_docs("oldtoken") == []
    assert paths_of(db.search_scan_docs("newtoken")) == {updated.path}


def test_fts5_delete_trigger_removes_index_entry(tmp_path, db):
    """Deleting a documents row removes the deleted content from the index.

    Search joins back to `documents`, so "no longer searchable" on its own cannot reveal a
    stale index entry. The deleted rowid is therefore reused by the next insert: a leaked
    entry would wrongly match the new document with the old content, so only the last two
    assertions actually exercise the delete trigger.
    """
    deleted = make_scan_doc(tmp_path, title="Deleted", content="staleunicorn", doc_name="deleted.md")
    db.insert_scan_doc(deleted)
    assert len(db.search_scan_docs("staleunicorn")) == 1

    # Database has no delete API: drop the row directly and let the delete trigger sync the index
    db.conn.execute("DELETE FROM documents WHERE path = ?", (str(deleted.path),))
    db.conn.commit()
    assert db.search_scan_docs("staleunicorn") == []

    reused = make_scan_doc(tmp_path, title="Reused", content="reusedtoken", doc_name="reused.md")
    db.insert_scan_doc(reused)

    assert db.search_scan_docs("staleunicorn") == []
    assert paths_of(db.search_scan_docs("reusedtoken")) == {reused.path}


def test_fts5_failed_insert_keeps_index_unchanged(tmp_path, db):
    """A failed insert must not leave a partially written index entry behind.

    The insert and its trigger-side index write are one write, so either both apply or
    neither does. The rowid the rejected insert consumed is reused by the next insert, so a
    leaked entry would make the rejected content searchable later. Also checks that the
    stored document is untouched and the database is still writable.
    """
    original = make_scan_doc(tmp_path, content="kepttoken", doc_name="original.md")
    db.insert_scan_doc(original)

    rejected = replace(original, title="Rejected", content="rejectedtoken", content_hash="rejected")
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_scan_doc(rejected)  # same path, so this violates the UNIQUE constraint

    later = make_scan_doc(tmp_path, content="latertoken", doc_name="later.md")
    db.insert_scan_doc(later)

    assert paths_of(db.search_scan_docs("kepttoken")) == {original.path}
    assert db.search_scan_docs("rejectedtoken") == []
    assert paths_of(db.search_scan_docs("latertoken")) == {later.path}
    assert db.get_scan_doc(str(original.path)) == original


def test_fts5_init_recovers_when_trigger_creation_fails(tmp_path, monkeypatch):
    """A failed initialization must be completable by opening the database again.

    The FTS table and its triggers are committed separately, so an error while creating the
    triggers leaves a file that already holds the FTS table. The next open therefore skips
    table creation, and only finishes the setup if it creates the triggers regardless - the
    document inserted after that open being searchable shows it did, instead of the file
    staying permanently unindexed.
    """
    db_path = tmp_path / "init_failure.db"

    def fail_creating_triggers(self):
        raise RuntimeError("trigger creation failed")

    monkeypatch.setattr(Database, "create_fts_table_triggers", fail_creating_triggers)
    with pytest.raises(RuntimeError):
        Database(str(db_path))
    monkeypatch.undo()

    db = Database(str(db_path))
    try:
        doc = make_scan_doc(tmp_path, content="recoverytoken", doc_name="recovery.md")
        db.insert_scan_doc(doc)

        assert paths_of(db.search_scan_docs("recoverytoken")) == {doc.path}
    finally:
        db.close()