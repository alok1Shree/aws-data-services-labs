from labs.lab06_textract.textract_parser import parse_lines, parse_key_values

RESPONSE = {"Blocks": [
    {"Id": "l1", "BlockType": "LINE", "Text": "Invoice No: 123", "Confidence": 99.1},
    {"Id": "l2", "BlockType": "LINE", "Text": "T0tal Due", "Confidence": 71.4},
    {"Id": "w1", "BlockType": "WORD", "Text": "Invoice"}, {"Id": "w2", "BlockType": "WORD", "Text": "No:"}, {"Id": "w3", "BlockType": "WORD", "Text": "123"},
    {"Id": "k1", "BlockType": "KEY_VALUE_SET", "EntityTypes": ["KEY"], "Relationships": [
        {"Type": "VALUE", "Ids": ["v1"]}, {"Type": "CHILD", "Ids": ["w1", "w2"]}]},
    {"Id": "v1", "BlockType": "KEY_VALUE_SET", "EntityTypes": ["VALUE"], "Relationships": [{"Type": "CHILD", "Ids": ["w3"]}]},
]}


def test_low_confidence_lines_flagged_for_review():
    out = parse_lines(RESPONSE)
    assert out["needs_review"] == ["T0tal Due"] and len(out["lines"]) == 2


def test_key_value_pairs_extracted():
    assert parse_key_values(RESPONSE) == {"Invoice No": "123"}
