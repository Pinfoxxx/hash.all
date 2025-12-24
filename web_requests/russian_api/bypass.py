import requests
import hashlib
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime) - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class YandexClusterClient:
    def __init__(self, public_url: str):
        """It works with directory on Yandex.Disk, where are the parts located"""
        self.dir = public_url
        self.files = []
        self.total_size = 0
        self.is_ready = False

        self._initialize_cluster()

    def _initialize_cluster(self):
        logger.info("Initializing files cluster from directory")
        self.files = []
        self.total_size = 0

        api = "https://cloud-api.yandex.net/v1/disk/public/resources"

        try:
            # Trying to have access to files in dir
            params = {"public_key": self.dir, "limit": 100}
            response = requests.get(api, params=params)

            if response.status_code != 200:
                logger.error(f"Directory access error: {response.status_code}")
                return

            data = response.json()
            if "_embedded" not in data:
                logger.error("This is not a directory or this empty")
                return

            items = data["_embedded"]["items"]

            # Filtering and sorting files
            file_items = [i for i in items if i["type"] == "file"]
            file_items.sort(key=lambda x: x["name"])

            if not file_items:
                logger.error("Directory is empty")
                return

            # Collecting direct links for every file
            for item in file_items:
                download_url = item.get("file")
                size = item.get("size", 0)
                name = item.get("name")

                if not download_url:
                    try:
                        response = requests.get(
                            api + "/download",
                            params={"public_key": self.dir, "path": "/" + name},
                        )
                        download_url = response.json().get("href")
                    except:
                        continue

                self.total_size += size
                # For deep debugging:
                # logger.info(f"Added: {name} ({size/1024**3:.2f} GB)")

            if self.files:
                self.is_ready = True
                logger.info(
                    f"Cluster is ready. Total files: {len(self.files)}. Total size: {self.total_size/1024**3:.2f} GB"
                )

        except Exception as e:
            logger.error(f"Cluster initialization error: {e}")

    def _read_chunk(self, virtual_offset: int, lenght: int = 512) -> bytes:
        """Reading bytes, determining the presence in files"""
        target = None
        local_offset = 0

        # Linear search
        for f in self.files:
            if f["start"] <= virtual_offset < f["end"]:
                target = f
                local_offset = virtual_offset - f["start"]
                break

        if not target:
            return b""

        headers = {"Range": f"bytes={local_offset}-{local_offset + lenght - 1}"}

        try:
            response = requests.get(target["url"], headers=headers, timeout=5)
            if response.status_code in [200, 206]:
                return response.content
        except:
            pass
        return b""

    def check_password(self, password: str) -> int:
        """Passwords checking"""
        if not password or not self.is_ready:
            return 0

        target_hash = hashlib.sha1(password.encode()).hexdigest().upper()

        low = 0
        high = self.total_size
        steps = 0

        while low < high and steps < 150:
            steps += 1
            mid = (low + high) // 2

            chunk = self._read_chunk(mid, 256)

            # Network error or end
            if not chunk:
                high = mid
                continue

            try:
                text = chunk.decode("ascii")

            # Middle of byte or garbage
            except UnicodeDecodeError:
                high = mid
                continue

            # Finding line border
            new_line = text.find("\n")
            if new_line == -1:
                high = mid
                continue

            line_start = new_line + 1
            line_end = text.find("\n", line_start)

            if line_end == -1:
                high = mid
                continue

            full_line = text[line_start:line_end].strip()

            if ":" not in full_line:
                high = mid
                continue

            try:
                hash, count = full_line.split(":")
                hash = hash.strip().upper()

                if hash == target_hash:
                    return int(count)
                elif hash < target_hash:
                    low = mid + line_start + len(full_line)
                else:
                    high = mid
            except:
                high = mid
        return 0
