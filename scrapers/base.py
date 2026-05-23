import logging
import random
import re
from dataclasses import dataclass, field
from typing import Optional

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
        self._session.headers["User-Agent"] = random.choice(USER_AGENTS)
        resp = self._session.get(url, timeout=15)
        resp.raise_for_status()
        self._last_url = resp.url
        self._last_soup = BeautifulSoup(resp.content, "html5lib")
        return self._last_soup

    def _resolve_url(self, href: str) -> str:
        from urllib.parse import urljoin
        return urljoin(self._last_url, href)

    def close(self):
        self._session.close()
