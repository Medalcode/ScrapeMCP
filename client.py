#!/usr/bin/env python3
import subprocess
import json
import sys
import time
import os
import select

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "server.py")
VENV_PYTHON = os.path.join(os.path.dirname(__file__), ".venv", "bin", "python")


class ScrapeMCPClient:
    def __init__(self):
        self.proc = None
        self._req_id = 0

    def start(self):
        self.proc = subprocess.Popen(
            [VENV_PYTHON, SERVER_SCRIPT],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "scrapemcp-client", "version": "1.0"},
        })
        self._recv()
        self._notification("notifications/initialized")

    def _send(self, method, params=None):
        self._req_id += 1
        msg = json.dumps({"jsonrpc": "2.0", "id": self._req_id, "method": method, "params": params or {}}) + "\n"
        self.proc.stdin.write(msg.encode())
        self.proc.stdin.flush()

    def _notification(self, method, params=None):
        msg = json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}}) + "\n"
        self.proc.stdin.write(msg.encode())
        self.proc.stdin.flush()

    def _recv(self, timeout=5):
        buf = b""
        deadline = time.time() + timeout
        while time.time() < deadline:
            r, _, _ = select.select([self.proc.stdout], [], [], 0.3)
            if r:
                chunk = self.proc.stdout.read1(4096)
                if not chunk: break
                buf += chunk
                if b"\n" in buf:
                    line, _ = buf.split(b"\n", 1)
                    return json.loads(line)
        try: return json.loads(buf.strip().split(b"\n")[0])
        except: return {}

    def call(self, tool, args=None):
        self._send("tools/call", {"name": tool, "arguments": args or {}})
        r = self._recv()
        content = r.get("result", {}).get("content", [])
        return "\n".join(c.get("text", "") for c in content)

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ScrapeMCP Client")
    parser.add_argument("command", nargs="?", default="demo",
                        choices=["demo", "scrape", "inspect", "tables", "list", "sitemap", "recursive", "export"])
    parser.add_argument("url", nargs="?", default="https://example.com")
    parser.add_argument("extra", nargs="*", default=[])
    args = parser.parse_args()

    client = ScrapeMCPClient()
    client.start()

    try:
        if args.command == "demo":
            print("=== ScrapeMCP Demo ===\n")

            print(f"📄 Inspect: {args.url}")
            print(client.call("inspect", {"url": args.url})[:800])
            print()

            print(f"📄 Scrape: {args.url}")
            print(client.call("scrape", {"url": args.url})[:500])
            print()

            print(f"🔗 Links from: {args.url}")
            data = json.loads(client.call("scrape", {"url": args.url, "selectors": {"links": "a"}}))
            links = data.get("links", [])
            print(f"  Found {len(links)} links")

        elif args.command == "scrape":
            print(client.call("scrape", {"url": args.url}))

        elif args.command == "inspect":
            print(client.call("inspect", {"url": args.url}))

        elif args.command == "tables":
            print(client.call("tables", {"url": args.url}))

        elif args.command == "list":
            if len(args.extra) < 2:
                print("Usage: client.py list <url> <item_selector> <fields_json>")
            else:
                print(client.call("scrape_list", {
                    "url": args.url,
                    "item_selector": args.extra[0],
                    "fields": args.extra[1],
                }))

        elif args.command == "sitemap":
            print(client.call("sitemap", {"url": args.url}))

        elif args.command == "recursive":
            if len(args.extra) < 3:
                print("Usage: client.py recursive <url> <link_sel> <item_sel> <fields_json> [max_pages]")
            else:
                print(client.call("scrape_recursive", {
                    "start_url": args.url,
                    "link_selector": args.extra[0],
                    "item_selector": args.extra[1],
                    "fields": args.extra[2],
                    "max_pages": int(args.extra[3]) if len(args.extra) > 3 else 10,
                }))

        elif args.command == "export":
            if not args.extra:
                print("Usage: client.py export <format> <json_data>")
            else:
                fmt = args.extra[0]
                data = " ".join(args.extra[1:]) if len(args.extra) > 1 else '{"test": "data"}'
                print(client.call("export", {"data": data, "format": fmt}))

    finally:
        client.stop()


if __name__ == "__main__":
    main()
