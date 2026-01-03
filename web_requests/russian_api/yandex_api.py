import requests
import logging
from typing import List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from models.yandex_model import FileMetadata

logger = logging.getLogger(__name__)


class YandexClient:
    """A class responsible for interacting with requests to the Yandex API"""

    API_BASE = "https://cloud-api.yandex.net/v1/disk/public/resources"
    DOWNLOAD_API = "https://cloud-api.yandex.net/v1/disk/public/resources/download"

    def __init__(self, public_folder: str):
        self.public_folder = public_folder
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        "Initializing session with automatic retries in case of network errors"
        session = requests.Session()
        attempts = Retry(
            total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=attempts))
        return session

    def get_files(self) -> List[FileMetadata]:
        "Get files list in public folder and displays the status or gives error"
        try:
            params = {"public_key": self.public_folder, "limit": 150}
            response = self.session.get(self.API_BASE, params=params, timeout=10)
            response.raise_for_status()

            items = response.json().get("_embedded", {}).get("items", [])

            files = [
                FileMetadata(
                    name=i["name"],
                    size=i.get("size", 0),
                    public_key=self.public_folder,
                    direct_url=i.get("file"),
                )
                for i in items
                if i["type"] == "file"
            ]
            files.sort(key=lambda x: x.name)
            return files

        except requests.RequestException as e:
            logger.error(f"Files list get error: {e}")
            return []

    def refresh_direct_url(self, file_data: FileMetadata) -> Optional[str]:
        "Refreshing bad download url or gives error"
        try:
            params = {"public_key": file_data.public_key, "path": "/" + file_data.name}
            response = self.session.get(self.DOWNLOAD_API, params=params, timeout=5)

            if response.status_code == 200:
                url = response.json().get("href")
                file_data.direct_url = url
                return url

        except requests.RequestException as e:
            logger.warning(f"Can't refresh link for {file_data.name}: {e}")
        return None

    def read_byte_chunk(self, url: str, start: str, end: int) -> Optional[bytes]:
        "Downloading chunk of file"
        headers = {"Range": f"bytes={start}-{end}"}
        try:
            response = self.session.get(url, headers=headers, timeout=5)

            if response.status_code in [200, 206]:
                return response.content

        except requests.RequestException:
            pass
        return None
