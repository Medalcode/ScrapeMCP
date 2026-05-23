def to_csv(data) -> str:
    if isinstance(data, list) and data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        lines = [",".join(headers)]
        for item in data:
            lines.append(",".join(str(item.get(h, "")).replace(",", "\\,") for h in headers))
        return "\n".join(lines)
    if isinstance(data, dict) and "items" in data and data["items"]:
        items = data["items"]
        if items and isinstance(items[0], dict):
            headers = list(items[0].keys())
            lines = [",".join(headers)]
            for item in items:
                lines.append(",".join(str(item.get(h, "")).replace(",", "\\,") for h in headers))
            return "\n".join(lines)
    import json
    return json.dumps(data, indent=2)


def to_markdown(data) -> str:
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
                result.append(to_markdown(value))
            elif isinstance(value, list):
                result.append(f"**{key}**: {', '.join(str(v) for v in value)}")
            else:
                result.append(f"**{key}**: {value}")
        return "\n\n".join(result)
    return str(data)
