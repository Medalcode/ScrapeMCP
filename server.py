import json
from mcp.server.fastmcp import FastMCP

from scrapers.page import PageScraper
from scrapers.table import TableScraper
from scrapers.list_scraper import ListScraper
from scrapers.sitemap import SitemapScraper
from exporters import to_csv, to_markdown

mcp = FastMCP("ScrapeMCP")

page_scraper = PageScraper()
table_scraper = TableScraper()
list_scraper = ListScraper()
sitemap_scraper = SitemapScraper()


@mcp.tool()
def scrape(url: str, selectors: dict[str, str] | None = None) -> str:
    result = page_scraper.scrape(url, selectors)
    if result.error:
        return f"Error: {result.error}"
    return json.dumps(result.data, indent=2, ensure_ascii=False)


@mcp.tool()
def inspect(url: str) -> str:
    result = page_scraper.inspect(url)
    if result.error:
        return f"Error: {result.error}"
    return json.dumps(result.data, indent=2, ensure_ascii=False)


@mcp.tool()
def tables(url: str, selector: str = "table") -> str:
    result = table_scraper.scrape_tables(url, selector)
    if result.error:
        return f"Error: {result.error}"
    return json.dumps(result.data, indent=2, ensure_ascii=False)


@mcp.tool()
def scrape_list(url: str, item_selector: str, fields: dict[str, str]) -> str:
    result = list_scraper.scrape_list(url, item_selector, fields)
    if result.error:
        return f"Error: {result.error}"
    return json.dumps(result.data, indent=2, ensure_ascii=False)


@mcp.tool()
def scrape_recursive(start_url: str, link_selector: str, item_selector: str,
                     fields: dict[str, str], max_pages: int = 10) -> str:
    result = list_scraper.scrape_recursive(
        start_url, link_selector, item_selector,
        fields, max_pages,
    )
    if result.error:
        return f"Error: {result.error}"
    return json.dumps(result.data, indent=2, ensure_ascii=False)


@mcp.tool()
def sitemap(url: str) -> str:
    result = sitemap_scraper.parse_sitemap(url)
    if result.error:
        return f"Error: {result.error}"
    data = result.data
    data["urls"] = data["urls"][:50]
    return json.dumps(data, indent=2, ensure_ascii=False)


@mcp.tool()
def scrape_sitemap(url: str, max_pages: int = 20) -> str:
    result = sitemap_scraper.scrape_sitemap(url, max_pages)
    if result.error:
        return f"Error: {result.error}"
    return json.dumps(result.data, indent=2, ensure_ascii=False)


@mcp.tool()
def export(data: str, format: str = "csv") -> str:
    parsed = json.loads(data)
    if format == "csv":
        return to_csv(parsed)
    if format == "json":
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    if format == "markdown":
        return to_markdown(parsed)
    return json.dumps(parsed, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
