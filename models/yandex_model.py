from dataclasses import dataclass
from typing import Optional


@dataclass
class FileMetadata:
    """File metadata structure"""

    name: str
    size: int
    public_key: str
    direct_url: Optional[str] = None
    start_hash: Optional[str] = None
