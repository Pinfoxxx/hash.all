import requests
import hashlib
import time
import logging

# Setting up simple logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(leveltime)s - %(message)s"
)
logger = logging.getLogger(__name__)


class YandexHIBPClient:
    def __init__(self, oauth_token: str, file_paths: list[str]):
        self.headers = {
            "Authorization": f"OAuth {oauth_token}",
            "Accept": "application/json",
        }
        self.files = []
        self.total_size = 0
        self.is_ready = False

        # Initialize connection
        self._initialize_database_links(file_paths)

    def _initialize_database_links(self, paths):
        logger.info("Initialize connection with passwords DB...")
        self.files = []
        self.total_size = 0

        try:
            for path in paths:
                link_url = "https://cloud-api.yandex.net/v1/disk/resorces/download"
                resp = requests.get(
                    link_url, headers=self.headers, params={"path": path}
                )

                if resp.status_code != 200:
                    logger.error(f"Link get failed for {path}: {resp.status_code}")
                    continue

                download_url = resp.json().get("href")

                # Get file size
                meta_url = "https://cloud-api.yandex.net/v1/disk/resources"
                meta_resp = requests.get(
                    meta_url, headers=self.headers, params={"path": path}
                )

                if meta_resp.status_code != 200:
                    logger.error(f"Failed to get matadata for {path}")
                    continue

                size = meta_resp.json().get("size", 0)

                self.files.append(
                    {
                        "url": download_url,
                        "size": size,
                        "start_byte": self.total_size,
                        "end_byte": self.total_size + size,
                    }
                )
                self.total_size += size
                logger.info(f"File {path} connected. Size: {size / (1024 ** 3):.2f} GB")

            if self.total_size > 0:
                self.is_ready = True
                logger.info(
                    f"Database is ready. Total virtual size: {self.total_size / (1024 ** 3):.2f} GB"
                )
            else:
                logger.error("Failed to connect any database file")

        except Exception as e:
            logger.error(f"Critical error while DB initialization: {e}")
