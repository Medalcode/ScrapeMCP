import re
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

from scrapers.base import BaseScraper, ScrapeResult


class SitemapScraper(BaseScraper):
    def parse_sitemap(self, url: str) -> ScrapeResult:
        try:
            sitemap_url = url.rstrip("/") + "/sitemap.xml"
            resp = self._session.get(sitemap_url, timeout=15)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            ns = re.sub(r"\{.*\}", "", root.tag)
            ns_match = re.match(r"\{(.*)\}", root.tag)
            ns = {"ns": ns_match.group(1)} if ns_match else {}

            urls = []
            if ns:
                for url_elem in root.findall(".//ns:url", ns):
                    loc = url_elem.find("ns:loc", ns)
                    if loc is not None and loc.text:
                        urls.append(loc.text)
                if not urls:
                    for sitemap_elem in root.findall(".//ns:sitemap", ns):
                        loc = sitemap_elem.find("ns:loc", ns)
                        if loc is not None and loc.text:
                            urls.append(loc.text)
            else:
                for url_elem in root.findall(".//url"):
                    loc = url_elem.find("loc")
                    if loc is not None and loc.text:
                        urls.append(loc.text)
                if not urls:
                    for sitemap_elem in root.findall(".//sitemap"):
                        loc = sitemap_elem.find("loc")
                        if loc is not None and loc.text:
                            urls.append(loc.text)

            return ScrapeResult(url=sitemap_url, status=200, data={
                "total": len(urls),
                "urls": urls,
            })
        except Exception as e:
            return ScrapeResult(url=url, status=0, error=str(e))

    def scrape_sitemap(self, url: str, max_pages: int = 20) -> ScrapeResult:
        sitemap_result = self.parse_sitemap(url)
        if sitemap_result.error:
            return sitemap_result

        all_urls = sitemap_result.data["urls"][:max_pages]
        pages = []
        for page_url in all_urls:
            try:
                soup = self._fetch(page_url)
                pages.append({
                    "url": self._last_url,
                    "title": soup.title.string.strip() if soup.title and soup.title.string else "",
                    "word_count": len(soup.get_text(separator=" ", strip=True).split()),
                })
            except Exception:
                pages.append({"url": page_url, "error": "Failed to fetch"})

        return ScrapeResult(url=url, status=200, data={
            "total_in_sitemap": sitemap_result.data["total"],
            "scraped": len(pages),
            "pages": pages,
        }, pages_scraped=len(pages))
