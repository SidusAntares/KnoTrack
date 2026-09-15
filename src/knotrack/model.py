from dataclasses import dataclass
from pathlib import Path

@dataclass
class ScanFile:
  title:str
  content:str
  size:int
  path:Path
