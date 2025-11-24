import ipaddress
import logging
import random
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("scrapemcp.base")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

_PRIVATE_BLOCKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

_BLOCKED_HOSTNAMES = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "metadata.google.internal", "169.254.169.254"}


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Scheme '{parsed.scheme}' not allowed (only http/https)")
    hostname = parsed.hostname or ""
    if hostname.lower() in _BLOCKED_HOSTNAMES:
        raise ValueError(f"Blocked hostname: {hostname}")
    try:
        addr = ipaddress.ip_address(hostname)
        for block in _PRIVATE_BLOCKS:
            if addr in block:
                raise ValueError(f"Blocked IP range: {hostname}")
    except ValueError:
        if hostname.lower().endswith(".internal") or hostname.lower().endswith(".local"):
            raise ValueError(f"Blocked hostname: {hostname}")


@dataclass
class ScrapeResult:
    url: str
    status: int
    data: dict | list | str | None = None
    error: Optional[str] = None
    pages_scraped: int = 1


class BaseScraper:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
        })
        self._last_soup: BeautifulSoup | None = None
        self._last_url: str = ""

    def _fetch(self, url: str) -> BeautifulSoup:
        logger.info("Fetching URL: %s", url)
        _validate_url(url)
        self._session.headers["User-Agent"] = random.choice(USER_AGENTS)
        resp = self._session.get(url, timeout=15)
        resp.raise_for_status()
        self._last_url = resp.url
        self._last_soup = BeautifulSoup(resp.content, "html5lib")
        return self._last_soup

    def close(self):
        self._session.close()
