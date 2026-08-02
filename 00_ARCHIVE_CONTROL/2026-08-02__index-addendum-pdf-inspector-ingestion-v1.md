# Index Addendum - PDF Inspector Ingestion v1

**Dato:** 2026-08-02  
**Status:** ARCHIVE_INDEX_ADDENDUM  
**Område:** document ingestion / PDF classification / Markdown extraction

## Authoritative routing

```text
research/pdf_ingestion/PDF_INSPECTOR_INGESTION_ARCHITECTURE_v1.md
research/pdf_ingestion/PDF_INSPECTOR_INGESTION_EXECUTION_STATE_v1.json
```

Implementation anchors:

```text
scripts/pdf_ingestion/pdf_ingest.py
tests/pdf_ingestion/build_minimal_pdf.py
tests/pdf_ingestion/test_pdf_ingest.py
.github/workflows/pdf-inspector-ingestion.yml
```

External source:

```text
https://github.com/firecrawl/pdf-inspector
pinned commit: a15ec2d68d51dbe6a39d1da688ec7a3f642d846c
```

## Binding interpretation

```yaml
integration_type: SHADOW_DOCUMENT_INFRASTRUCTURE
openai_api_required: false
user_action_required_for_installation: false
raw_pdf_auto_commit: false
markdown_auto_commit: false
ocr_performed: false
vision_interpretation_performed: false
framework_state_changed: false
portfolio_action_changed: false
```

The integration creates an auditable preprocessing route. It does not make extracted Markdown authoritative over the original PDF and does not interpret charts, diagrams or missing scanned pages.
