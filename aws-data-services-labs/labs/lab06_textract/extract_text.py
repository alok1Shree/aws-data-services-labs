"""Run Textract on an S3 document (JPEG/PNG/single-page PDF) and save structured output back to S3.
Multi-page PDFs need the async APIs (start_document_analysis + SNS/polling) - see README."""
import json
import sys

from common.aws import client
from labs.lab06_textract.textract_parser import parse_key_values, parse_lines


def extract(bucket: str, key: str, textract=None, s3=None) -> dict:
    textract = textract or client("textract")
    s3 = s3 or client("s3")
    doc = {"S3Object": {"Bucket": bucket, "Name": key}}
    text = textract.detect_document_text(Document=doc)
    forms = textract.analyze_document(Document=doc, FeatureTypes=["FORMS"])
    result = {"source": f"s3://{bucket}/{key}", **parse_lines(text), "fields": parse_key_values(forms)}
    s3.put_object(Bucket=bucket, Key=f"extracted/{key}.json", Body=json.dumps(result).encode(), ContentType="application/json")
    return result


if __name__ == "__main__":
    print(json.dumps(extract(sys.argv[1], sys.argv[2]), indent=2))
