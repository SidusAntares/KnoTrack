from knotrack import cli
from knotrack import Database
import sys

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
    db = cli.Database(db)
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

def test_cli_search_no_matches(tmp_path):
    # Run the search command with a query that has no matches
    cli.main(["search", "Nonexistent Document",
              "--db", str(tmp_path / "test.db")])

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

def test_cli_main_no_command(tmp_path, capsys):
    # Run the CLI with no command
    cli.main([])
    captured = capsys.readouterr()
    assert (
        "Available commands" in captured.out
            ), "Help message was not displayed when no command was provided."
    assert (
        "Title:" not in captured.out
            ), "Unexpected search results found."


