from pathlib import Path
from .model import ScanDoc
import hashlib
support_suffix = [".md"]
support_ignore_dir = [".git",".vscode","__pycache__"]

def filter_doc(path: Path)->bool:
    f = Path(path)
    if not f.exists():
        raise FileNotFoundError(f"File {path} does not exist.")
    elif f.is_file():
        if  f.suffix in support_suffix:return True
        else:
            print(f"Not support file {path}.")
            return False
    else:
        assert f.is_dir()
        if f.name in support_ignore_dir or f.name.startswith("."):
            print(f"Ignore directory {path}.")
            return False
        return True

def scan_doc(path: Path):
    f = Path(path)
    if not filter_doc(f):
        return
    if f.is_dir():
        for file in sorted(f.iterdir(),key = lambda x : x.name.casefold()):
            yield from scan_doc(file)
    else:
        content = f.read_text(encoding="utf-8")
        scanfile = ScanDoc(
            title = f.stem,
            content = content,
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest(),
            size = f.stat().st_size,
            path = f
        )
        yield scanfile


if __name__ == "__main__":
    for scanfile in scan_doc(Path(r"D:\All_Documents\note\programm\Sidus-Programme-Notes\学科笔记\专业课\计算机网络")):
        print(scanfile)