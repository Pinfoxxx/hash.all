import hashlib
import requests
import time


class HIBPClient:
    # Setting API limits
    def __init__(self):
        self.last_request_time = 0
        self.min_request_interval = 1.6

    # Another limits / counting time / antiblock-guard
    def _rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def check_password_breach(self, password: str) -> int:
        # Validate password
        if not password:
            return -1

        # Encoding password if everything is fine / send prefix to the server / save local suffix
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]

        # Call rate limiter
        self._rate_limit()

        # Save HTTP-request or exception with 10 second timeout / API-request
        try:
            response = requests.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                timeout=10,
                headers={"User-Agent": "hash.all-Password-Checker"},
            )
            response.raise_for_status()

            # Local match search
            hashes = (line.split(":") for line in response.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    return int(count)  # Return count of leaks
            return 0  # Return save password

        except requests.RequestException as e:
            print(f"Have I Been Pwned API error: {e}")
            return -1  # API or connection error
