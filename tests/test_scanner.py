from knotrack.scanner import  scan_doc as scanner
import pytest

def test_scan_simple_md(tmp_path):
    md_path = tmp_path / "test_scan_simple_md.md"
    md_path.write_text("# Test\n\nThis is a test file.")
    scanfiles = list(scanner(md_path))
    assert len(scanfiles) == 1
    assert scanfiles[0].title == "test_scan_simple_md"
    assert scanfiles[0].size > 0
    assert scanfiles[0].size == md_path.stat().st_size
    assert scanfiles[0].path.name == "test_scan_simple_md.md"

def test_scan_nested_dir_md(tmp_path):
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    md_path = nested_dir / "test_scan_nested_dir_md.md"
    md_path.write_text("# Test\n\nThis is a test file in a nested directory.")
    scanfiles = list(scanner(tmp_path))
    assert len(scanfiles) == 1
    assert scanfiles[0].title == "test_scan_nested_dir_md"
    assert scanfiles[0].size > 0
    assert scanfiles[0].size == md_path.stat().st_size
    assert scanfiles[0].path.name == "test_scan_nested_dir_md.md"

def test_scan_ignore_file(tmp_path):
    txt_path = tmp_path / "test_scan_ignore_file.txt"
    txt_path.write_text("This is a test file that should be ignored.")
    scanfiles = list(scanner(tmp_path))
    assert len(scanfiles) == 0

def test_scan_ignore_dir(tmp_path):
    for test_dir in [".git",".vscode","__pycache__"]:
        ignore_dir = tmp_path / f"{test_dir}"
        ignore_dir.mkdir()
        test_md = ignore_dir / f"test_scan_ignore_dir_{test_dir}.md"
        test_md.write_text("# Test\n\nThis is a test file in an ignored directory.")
        scanfiles = list(scanner(tmp_path))
        assert len(scanfiles) == 0

def test_scan_output_order(tmp_path):
    md_path1 = tmp_path / "b_test_scan_output_order.md"
    md_path1.write_text("# Test\n\nThis is a test file.")
    md_path2 = tmp_path / "a_test_scan_output_order.md"
    md_path2.write_text("# Test\n\nThis is another test file.")
    scanfiles = list(scanner(tmp_path))
    assert len(scanfiles) == 2
    assert scanfiles[0].title == "a_test_scan_output_order"
    assert scanfiles[1].title == "b_test_scan_output_order"

def test_scan_chinese_utf_8(tmp_path):
    md_path = tmp_path / "测试中文utf-8读取.md"
    md_path.write_text("# 测试\n\n这是一个测试文件。",encoding="utf-8")
    scanfiles = list(scanner(tmp_path))
    assert len(scanfiles) == 1
    assert scanfiles[0].title == "测试中文utf-8读取"
    assert scanfiles[0].size > 0
    assert scanfiles[0].size == md_path.stat().st_size
    assert scanfiles[0].content == "# 测试\n\n这是一个测试文件。"

def test_scan_absence_path(tmp_path):
    absence_path = tmp_path / "non_existent_file.md"
    with pytest.raises(FileNotFoundError) :
        list(scanner(absence_path))

