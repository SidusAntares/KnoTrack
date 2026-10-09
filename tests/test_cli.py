from knotrack import cli
from knotrack import Database


def snippet_from(output):
    """The text the CLI prints after its `Snippet:` label."""
    return output.split("Snippet:", 1)[1]


# ---------------------------------------------------------------------------
# Index command
# ---------------------------------------------------------------------------

def test_cli_index(tmp_path):
    # Create a temporary markdown file
    temp_doc = tmp_path /"test_dir" / "test.md"
    temp_doc.parent.mkdir(parents=True, exist_ok=True)
    temp_doc.write_text("# Test Document\nThis is a test document.")

    # Run the index command
    cli.main(["index", str(tmp_path /"test_dir"),
              "--db", str(tmp_path / "test.db")])

    # Check if the database file was created
    db = tmp_path / "test.db"
    assert db.exists(), "Database file was not created."
    db = Database(db)
    scan_doc = db.get_scan_doc(str(temp_doc))
    assert scan_doc is not None, "Document was not indexed."
    db.close()

def test_cli_index_multiple_paths(tmp_path):
    temp_doc1 = tmp_path / "test_dir1" / "test1.md"
    temp_doc1.parent.mkdir(parents=True, exist_ok=True)
    temp_doc1.write_text("# Test Document 1\nThis is a test document.")

    temp_doc2 = tmp_path / "test_dir2" / "test2.md"
    temp_doc2.parent.mkdir(parents=True, exist_ok=True)
    temp_doc2.write_text("# Test Document 2\nThis is a test document.")

    # Run the index command
    cli.main(["index", str(tmp_path /"test_dir1"), str(tmp_path /"test_dir2"),
              "--db", str(tmp_path / "test.db")])

    # Check if the database file was created
    db = tmp_path / "test.db"
    assert db.exists(), "Database file was not created."
    db = Database(db)
    scan_doc1 = db.get_scan_doc(str(temp_doc1))
    assert scan_doc1 is not None, "Document 1 was not indexed."
    scan_doc2 = db.get_scan_doc(str(temp_doc2))
    assert scan_doc2 is not None, "Document 2 was not indexed."
    db.close()

# ---------------------------------------------------------------------------
# Search command
# ---------------------------------------------------------------------------

def test_cli_search(tmp_path, capsys):
    # Create a temporary markdown file and index it
    temp_doc = tmp_path / "test_dir" / "test.md"
    temp_doc.parent.mkdir(parents=True, exist_ok=True)
    temp_doc.write_text("# Test Document\nThis is a test document.")
    cli.main(["index", str(tmp_path /"test_dir"),
              "--db", str(tmp_path / "test.db")])

    # Run the search command
    cli.main(["search", "Test Document",
              "--db", str(tmp_path / "test.db")])
    # Capture the output and check if the document was found
    captured = capsys.readouterr()
    assert (
        str(temp_doc) in captured.out
    ), "Document was not found in search results."

def test_cli_search_no_matches(tmp_path, capsys):
    # Run the search command with a query that has no matches
    cli.main(["search", "Nonexistent Document",
              "--db", str(tmp_path / "test.db")])
    captured = capsys.readouterr()
    assert (
            "Title:" not in captured.out
                ), "Unexpected search results found."

def test_cli_search_with_limit(tmp_path, capsys):
    temp_doc1 = tmp_path / "test1.md"
    temp_doc2 = tmp_path / "test2.md"
    temp_doc3 = tmp_path / "test3.md"
    temp_doc1.write_text("# Test Document 1\nThis is a test document.")
    temp_doc2.write_text("# Test Document 2\nThis is a test document.")
    temp_doc3.write_text("# Test Document 3\nThis is a test document.")

    cli.main(["index", str(temp_doc1), str(temp_doc2), str(temp_doc3),
              "--db", str(tmp_path / "test.db")])

    # Run the search command with a limit
    cli.main(["search", "Test Document",
              "--db", str(tmp_path / "test.db"), "--limit", "2"])

    captured = capsys.readouterr()
    # Check that only 2 results are returned
    assert (
        captured.out.count("Title:") == 2
            ),"Search results exceeded the specified limit."

def test_cli_search_snippet_shows_content_match(tmp_path, capsys):
    """A match inside the body is printed as part of the snippet.

    The search command prints the snippet so a user can see why a document matched, so a
    query that occurs in the body has to appear in the printed Snippet text.
    """
    doc_path = tmp_path / "docs" / "notes.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("# Notes\nSQLite supports full text search using FTS5.")
    cli.main(["index", str(tmp_path / "docs"), "--db", str(tmp_path / "test.db")])

    cli.main(["search", "FTS5", "--db", str(tmp_path / "test.db")])
    captured = capsys.readouterr()

    assert str(doc_path) in captured.out
    assert "FTS5" in snippet_from(captured.out)

def test_cli_search_snippet_omits_title_only_match(tmp_path, capsys):
    """A title-only match lists the document with the query left out of the snippet.

    A document's title is its file name, so naming a file after the query matches it through
    the title while its body stays free of the query. The command must still print the
    document, with the query appearing in the Title line rather than in the snippet.
    """
    doc_path = tmp_path / "docs" / "FTS5-notes.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("Nothing about indexing here.")
    cli.main(["index", str(tmp_path / "docs"), "--db", str(tmp_path / "test.db")])

    cli.main(["search", "FTS5", "--db", str(tmp_path / "test.db")])
    captured = capsys.readouterr()

    assert "Title: FTS5-notes" in captured.out
    assert "FTS5" not in snippet_from(captured.out)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def test_cli_main_no_command(capsys):
    # Run the CLI with no command
    cli.main([])
    captured = capsys.readouterr()
    assert (
        "Available commands" in captured.out
            ), "Help message was not displayed when no command was provided."
    assert (
        "Title:" not in captured.out
            ), "Unexpected search results found."


