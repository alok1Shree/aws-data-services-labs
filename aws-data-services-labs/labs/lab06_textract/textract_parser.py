"""Pure functions that turn raw Textract responses into usable data (unit-testable without AWS)."""


def parse_lines(response: dict, min_confidence: float = 90.0) -> dict:
    lines = [b for b in response.get("Blocks", []) if b["BlockType"] == "LINE"]
    return {
        "lines": [{"text": b["Text"], "confidence": round(b["Confidence"], 2)} for b in lines],
        "needs_review": [b["Text"] for b in lines if b["Confidence"] < min_confidence],
    }


def _text_of(block: dict, by_id: dict) -> str:
    words = []
    for rel in block.get("Relationships", []):
        if rel["Type"] == "CHILD":
            words += [by_id[i]["Text"] for i in rel["Ids"] if by_id[i]["BlockType"] == "WORD"]
    return " ".join(words)


def parse_key_values(response: dict) -> dict:
    """FORMS analysis: link KEY_VALUE_SET blocks (EntityType KEY) to their VALUE blocks."""
    by_id = {b["Id"]: b for b in response.get("Blocks", [])}
    result = {}
    for block in by_id.values():
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
            key = _text_of(block, by_id)
            for rel in block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    for vid in rel["Ids"]:
                        result[key.rstrip(": ")] = _text_of(by_id[vid], by_id)
    return result
