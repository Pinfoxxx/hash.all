import logging

from .hash_search import HashDBSearch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    PUBLIC_URL = "https://disk.yandex.ru/d/O22Pp0Anlf0rRA"

    db = HashDBSearch(PUBLIC_URL)

    if db.is_ready:
        test = "123456"
        count = db.check_password(test)

        if count > 0:
            print(f"Password '{test}' found in the database {count} times.")
        else:
            print(f"Password '{test}' not found.")
