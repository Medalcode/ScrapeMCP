import re
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup


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
            "User-Agent": "Mozilla/5.0 (compatible; ScrapeMCP/1.0)",
        })
        self._last_soup: BeautifulSoup | None = None
        self._last_url: str = ""

    def _fetch(self, url: str) -> BeautifulSoup:
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
