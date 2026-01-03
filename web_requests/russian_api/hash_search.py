import logging
import hashlib

from typing import List, Optional

from models.yandex_model import FileMetadata
from .yandex_api import YandexClient

logger = logging.getLogger(__name__)


class HashDBSearch:
    """Database hash finder"""

    CHUNK_SIZE = 256
    MAX_STEPS = 60

    def __init__(self, public_folder: str):
        self.client = YandexClient(public_folder)
        self.files: List[FileMetadata] = []
        self.is_ready = False

        self._initialize()

    def _initialize(self):
        "Initializing with error handler"
        logger.info("Database initializing...")
        self.files = self.client.get_files()

        if self.files:
            self.is_ready = True
            logger.info(f"Database is ready. Loaded parts: {len(self.files)}")
        else:
            logger.error("Initializing error: folder empty or can't be reached.")

    def _ensure_direct_url(self, file_id: int) -> Optional[str]:
        "Confirms the existence of the URL or sends a repeated request"
        f = self.files[file_id]

        if f.direct_url:
            return f.direct_url
        return self.client.refresh_direct_url(f)

    def _get_file_start_hash(self, file_id: int) -> str:
        "Determines which hash the file starts with"
        f = self.files[file_id]

        if f.start_hash:
            return f.start_hash

        url = self._ensure_direct_url(file_id)
        if not url:
            return "0" * 40

        chunk = self.client.read_byte_chunk(url, 0, 60)
        if chunk:
            try:
                line = chunk.decode("ascii", errors="ignore").split("\n")[0].strip()
                if ":" in line:
                    h = line.split(":")[0]
                    f.start_hash = h
                    return h
            except Exception:
                pass
        return "0" * 40

    def _find_target_index(self, target_hash: str) -> int:
        "Binary search for the required file"
        low = 0
        high = len(self.files) - 1
        best_id = -1

        while low <= high:
            mid = (low + high) // 2
            mid_hash = self._get_file_start_hash(mid)

            if mid_hash <= target_hash:
                best_id = mid
                low = mid + 1
            else:
                high = mid - 1

        return best_id

    def _search_inside(self, file_id: int, target_hash: str) -> int:
        "Binary search in the required file"
        url = self._ensure_direct_url(file_id)
        if not url:
            return 0

        low = 0
        high = self.files[file_id].size
        steps = 0

        while low < high and steps < self.MAX_STEPS:
            steps += 1
            mid = (low + high) // 2

            chunk = self.client.read_byte_chunk(url, mid, mid + self.CHUNK_SIZE)
            if not chunk:
                high = mid
                continue

            try:
                text = chunk.decode("ascii", errors="ignore")
            except Exception:
                high = mid
                continue

            first_in_nl = text.find("\n")
            if first_in_nl == -1:
                high = mid
                continue

            line_start = first_in_nl + 1
            next_in_nl = text.find("\n", line_start)

            if next_in_nl == -1:
                high = mid
                continue

            full_line = text[line_start:next_in_nl].strip()

            if ":" not in full_line:
                high = mid
                continue

            try:
                current_hash, count_str = full_line.split(":", 1)
                current_hash = current_hash.strip().upper()

                if current_hash == target_hash:
                    return int(count_str)
                elif current_hash < target_hash:
                    low = mid + line_start + len(full_line)
                else:
                    high = mid
            except ValueError:
                high = mid
        return 0

    def check_password(self, password: str) -> int:
        "Checking password"
        if not password or not self.is_ready:
            return 0

        target_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()

        file_id = self._find_target_index(target_hash)
        if file_id == -1:
            return 0

        logger.info(
            f"Checking hash {target_hash[:8]}... in file {self.files[file_id].name}"
        )
        return self._search_inside(file_id, target_hash)
