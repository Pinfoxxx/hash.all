import requests
import hashlib
import logging

# Setting up logger configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", force=True
)
logger = logging.getLogger(__name__)


class YandexClusterClient:
    def __init__(self, public_folder_url: str):
        self.public_folder = public_folder_url
        self.files = []
        self.is_ready = False

        # Cache for the first hashes of files to avoid redundant requests
        self.start_hashes_cache = {}

        self._initialize_cluster()

    def _initialize_cluster(self):
        logger.info("Initializing: Fetching file list from Yandex.Disk...")
        self.files = []

        api_base = "https://cloud-api.yandex.net/v1/disk/public/resources"

        try:
            params = {"public_key": self.public_folder, "limit": 100}
            resp = requests.get(api_base, params=params)

            if resp.status_code != 200:
                logger.error(f"Error accessing folder: {resp.status_code}")
                return

            items = resp.json().get("_embedded", {}).get("items", [])

            # Filter only files and sort them by name
            file_items = [i for i in items if i["type"] == "file"]
            file_items.sort(key=lambda x: x["name"])

            if not file_items:
                logger.error("Folder is empty.")
                return

            for item in file_items:
                # We store metadata. Direct URL will be fetched lazily when needed.
                self.files.append(
                    {
                        "name": item["name"],
                        "size": item.get("size", 0),
                        "public_url": self.public_folder,
                        "direct_url": item.get(
                            "file"
                        ),  # Might be None, will refresh if needed
                    }
                )

            if self.files:
                self.is_ready = True
                logger.info(f"Cluster ready: {len(self.files)} database parts found.")

        except Exception as e:
            logger.error(f"Initialization error: {e}")

    def _get_direct_url(self, file_idx):
        """Gets or refreshes the direct download link for a specific file."""
        f = self.files[file_idx]

        # Check if the link exists (we assume it's valid for performance)
        if f.get("direct_url"):
            return f["direct_url"]

        # Fetch a new link if missing
        try:
            api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
            resp = requests.get(
                api_url, params={"public_key": f["public_url"], "path": "/" + f["name"]}
            )
            if resp.status_code == 200:
                url = resp.json().get("href")
                self.files[file_idx]["direct_url"] = url
                return url
        except Exception as e:
            logger.error(f"Failed to get link for {f['name']}: {e}")
        return None

    def _get_start_hash(self, file_idx):
        """Downloads the first line of the file to determine its starting hash."""
        if file_idx in self.start_hashes_cache:
            return self.start_hashes_cache[file_idx]

        url = self._get_direct_url(file_idx)
        if not url:
            # Fallback for error cases
            return "0000000000000000000000000000000000000000"

        try:
            # Reading the first 60 bytes
            r = requests.get(url, headers={"Range": "bytes=0-60"}, timeout=3)
            if r.status_code in [200, 206]:
                line = r.text.split("\n")[0].strip()
                if ":" in line:
                    h = line.split(":")[0]
                    self.start_hashes_cache[file_idx] = h
                    return h
        except Exception:
            pass

        return None  # Read error

    def _find_correct_file_index(self, target_hash):
        """
        STAGE 1: Binary search to find the correct FILE index.
        Determines which file contains the target_hash based on start hashes.
        """
        low = 0
        high = len(self.files) - 1
        best_file_idx = -1

        while low <= high:
            mid = (low + high) // 2

            # Get the starting hash of the mid file
            mid_start_hash = self._get_start_hash(mid)

            if not mid_start_hash:
                # If file is unreadable (like part_008), try to narrow down to previous files
                # or just skip it. Going left is a safe fallback.
                high = mid - 1
                continue

            if target_hash < mid_start_hash:
                # Target hash is smaller than this file's start -> it's in previous files
                high = mid - 1
            else:
                # Target hash is >= this file's start -> it's in this file or next ones
                best_file_idx = mid  # Store as candidate
                low = mid + 1

        return best_file_idx

    def _search_in_file(self, file_idx, target_hash):
        """
        STAGE 2: Binary search INSIDE the specific file.
        """
        url = self._get_direct_url(file_idx)
        if not url:
            return 0

        file_size = self.files[file_idx]["size"]
        low = 0
        high = file_size

        steps = 0

        while low < high and steps < 60:
            steps += 1
            mid = (low + high) // 2

            # Reading a chunk
            try:
                r = requests.get(
                    url, headers={"Range": f"bytes={mid}-{mid+255}"}, timeout=5
                )
                chunk = r.content
            except:
                # Network error -> narrow search (safe fallback)
                high = mid
                continue

            if not chunk:
                high = mid
                continue

            try:
                text = chunk.decode("ascii", errors="ignore")
            except:
                high = mid
                continue

            nl = text.find("\n")
            if nl == -1:
                high = mid
                continue

            line_start = nl + 1
            line_end = text.find("\n", line_start)

            if line_end == -1:
                high = mid
                continue

            full_line = text[line_start:line_end].strip()

            if ":" not in full_line:
                high = mid
                continue

            try:
                h, c = full_line.split(":")
                h = h.strip().upper()

                if h == target_hash:
                    return int(c)
                elif h < target_hash:
                    # Target is greater -> go right (down)
                    low = mid + line_start + len(full_line)
                else:
                    # Target is smaller -> go left (up)
                    high = mid
            except:
                high = mid

        return 0

    def check_password(self, password: str) -> int:
        """Main check method"""
        if not password or not self.is_ready:
            return 0

        target_hash = hashlib.sha1(password.encode()).hexdigest().upper()

        # 1. Find the correct file (e.g., part_011)
        file_idx = self._find_correct_file_index(target_hash)

        if file_idx == -1:
            return 0

        logger.info(
            f"Hash {target_hash[:6]}... -> Searching in file: {self.files[file_idx]['name']}"
        )

        # 2. Search inside that specific file
        return self._search_in_file(file_idx, target_hash)
