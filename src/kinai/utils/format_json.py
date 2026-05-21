import json

def format_segment(seg):
    """Formatea un segmento como string compacto."""
    return (
        "{ "
        + ", ".join(
            f"\"{k}\": {json.dumps(v, ensure_ascii=False)}"
            for k, v in seg.items()
        )
        + " }"
    )

def format_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    lines.append("[")

    for i, item in enumerate(data):
        lines.append("  {")
        lines.append(f'    "url": {json.dumps(item["url"], ensure_ascii=False)},')
        lines.append(f'    "title": {json.dumps(item["title"], ensure_ascii=False)},')
        lines.append('    "segments": [')
        
        for j, seg in enumerate(item["segments"]):
            comma = "," if j < len(item["segments"]) - 1 else ""
            lines.append(f"      {format_segment(seg)}{comma}")
        
        lines.append("    ],")
        
        # AÑADIR METADATA AQUÍ
        metadata = '    "metadata": {'
        metadata_items = []
        for k, v in item.get("metadata", {}).items():
            metadata_items.append(f'"{k}": {json.dumps(v, ensure_ascii=False)}')
        metadata += (", ".join(metadata_items))
        metadata += ("}")
        lines.append(metadata)
        lines.append("  }" + ("," if i < len(data) - 1 else ""))

    lines.append("]")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("✓ JSON formateado con metadata incluida")