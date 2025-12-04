# ScrapeMCP — Web Scraping MCP Server

Servidor MCP para extracción estructurada de datos web. Scrapea páginas, tablas, listas, sitemaps y más. Incluye protección SSRF integrada.

## Features / Funcionalidades

| Tool / Herramienta | Description / Descripción |
|---|---|
| `scrape` | Extrae contenido de una URL usando selectores CSS personalizados |
| `inspect` | Analiza la estructura de una página (meta tags, headings, links, images, forms, scripts) |
| `tables` | Extrae todas las tablas HTML de una página |
| `scrape_list` | Extrae una lista de items con campos personalizados desde selectores CSS |
| `scrape_recursive` | Navega páginas enlazadas recursivamente extrayendo datos |
| `sitemap` | Parsea el sitemap.xml de un sitio web |
| `scrape_sitemap` | Scrapea todas las URLs de un sitemap |
| `export` | Exporta datos a CSV, Markdown o JSON |

## SSRF Protection / Protección SSRF

El servidor bloquea automáticamente accesos a:

- IPs privadas (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
- Localhost/loopback (`127.0.0.0/8`, `::1`)
- Link-local (`169.254.0.0/16`, `fe80::/10`)
- Hostnames bloqueados: `localhost`, `metadata.google.internal`, `169.254.169.254`
- Dominios `.internal` y `.local`

Solo permite esquemas `http://` y `https://`.

## Tech Stack

- **Python** — `>=3.11`
- **Framework**: `mcp` (FastMCP) via stdio JSON-RPC
- **HTTP**: `requests` + `httpx`
- **Parsing**: `beautifulsoup4` + `html5lib`
- **Export**: CSV (sanitized), Markdown, JSON

## Quick Start

```bash
# Instalar dependencias
pip install mcp requests beautifulsoup4 html5lib httpx

# Ejecutar servidor
python server.py
```

### Ejemplos

```python
# Scrapear página completa
result = await session.call_tool("scrape", {"url": "https://example.com"})

# Scrapear con selectores personalizados
result = await session.call_tool("scrape", {
    "url": "https://example.com",
    "selectors": {"title": "h1", "price": ".price"}
})

# Inspeccionar estructura de página
result = await session.call_tool("inspect", {"url": "https://example.com"})

# Extraer tablas
result = await session.call_tool("tables", {
    "url": "https://example.com",
    "selector": "table"
})

# Scrapear lista
result = await session.call_tool("scrape_list", {
    "url": "https://example.com/items",
    "item_selector": ".item",
    "fields": {"name": "h2", "price": ".price"}
})

# Scrapear recursivamente
result = await session.call_tool("scrape_recursive", {
    "start_url": "https://example.com/blog",
    "link_selector": "a.post-link",
    "item_selector": "article",
    "fields": {"title": "h1", "content": "p"},
    "max_pages": 10
})

# Exportar a CSV
result = await session.call_tool("export", {
    "data": '[{"name": "Alice", "age": 30}]',
    "format": "csv"
})
```

## Project Structure

```
scrapemcp/
├── server.py              # MCP server entry point (tools)
├── scrapers/
│   ├── __init__.py
│   ├── base.py            # BaseScraper, ScrapeResult, SSRF validation
│   ├── page.py            # PageScraper (scrape, inspect)
│   ├── table.py           # TableScraper (tables)
│   ├── list_scraper.py    # ListScraper (scrape_list, scrape_recursive)
│   └── sitemap.py         # SitemapScraper (sitemap, scrape_sitemap)
├── exporters.py           # CSV, Markdown, JSON export
├── client.py              # Test client CLI
└── pyproject.toml
```
