"""The record type every stage of the pipeline passes around.

A ScanDoc is produced by scanning, stored by the database and handed back by search, so a
field added here reaches all three.
"""

from dataclasses import dataclass
from pathlib import Path

@dataclass
class ScanDoc:
  title: str          # file name without its suffix, used as the document title
  content: str        # full document text
  content_hash: str   # hash of the content, so re-indexing can skip unchanged documents
  size: int           # file size in bytes
  path: Path          # absolute path, unique per document
