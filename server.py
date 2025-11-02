import json
from mcp.server.fastmcp import FastMCP

from scrapers.page import PageScraper
from scrapers.table import TableScraper
from scrapers.list_scraper import ListScraper
from scrapers.sitemap import SitemapScraper

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
        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
            headers = list(parsed[0].keys())
            lines = [",".join(headers)]
            for item in parsed:
                lines.append(",".join(str(item.get(h, "")).replace(",", "\\,") for h in headers))
            return "\n".join(lines)
        elif isinstance(parsed, dict) and "items" in parsed and parsed["items"]:
            items = parsed["items"]
            if items and isinstance(items[0], dict):
                headers = list(items[0].keys())
                lines = [",".join(headers)]
                for item in items:
                    lines.append(",".join(str(item.get(h, "")).replace(",", "\\,") for h in headers))
                return "\n".join(lines)
        return json.dumps(parsed, indent=2)
    if format == "json":
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    if format == "markdown":
        return _to_markdown(parsed)
    return json.dumps(parsed, indent=2)


def _to_markdown(data) -> str:
    if isinstance(data, list) and data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for item in data:
            lines.append("| " + " | ".join(str(item.get(h, "")) for h in headers) + " |")
        return "\n".join(lines)
    if isinstance(data, dict):
        result = []
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                result.append(f"## {key}")
                result.append(_to_markdown(value))
            elif isinstance(value, list):
                result.append(f"**{key}**: {', '.join(str(v) for v in value)}")
            else:
                result.append(f"**{key}**: {value}")
        return "\n\n".join(result)
    return str(data)


if __name__ == "__main__":
    mcp.run(transport="stdio")
