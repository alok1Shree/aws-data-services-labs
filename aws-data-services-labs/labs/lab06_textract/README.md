# Lab 06 — Textract document extraction

`extract_text.py` calls `DetectDocumentText` (lines + confidence) and `AnalyzeDocument` with `FORMS` (key/value pairs, e.g. *Invoice No: 123*), then stores JSON under `extracted/` in the bucket.

## Run
```bash
aws cloudformation deploy --template-file template.yaml --stack-name lab06-textract
aws s3 cp sample-invoice.png s3://<BucketName>/docs/sample-invoice.png     # use your own non-sensitive sample
python -m labs.lab06_textract.extract_text <BucketName> docs/sample-invoice.png
```
Cleanup: empty the bucket, delete the stack.

## Design notes
- Treat OCR output as **probabilistic**: route low-confidence lines (`needs_review`) to a human instead of trusting them.
- Sync APIs handle images / single-page PDFs; multi-page PDFs use `StartDocumentAnalysis` + SNS completion + `GetDocumentAnalysis` pagination (use Step Functions from Lab 03 to orchestrate).
- Textract is priced per page and by feature (FORMS costs more than plain text) — only request features you use.
- Never run real customer documents through a lab account: IDs and bank statements are regulated data.
