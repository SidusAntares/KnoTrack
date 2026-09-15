from dataclasses import dataclass
from pathlib import Path

@dataclass
class ScanDoc:
  title:str
  content:str
  content_hash:str
  size:int
  path:Path

