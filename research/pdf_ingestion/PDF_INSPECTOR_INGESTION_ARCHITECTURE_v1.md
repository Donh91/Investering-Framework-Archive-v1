# PDF INSPECTOR INGESTION ARCHITECTURE v1

**Dato:** 2026-08-02  
**Status:** SHADOW-ONLY DOCUMENT INGESTION INFRASTRUCTURE  
**Upstream:** `https://github.com/firecrawl/pdf-inspector`  
**Pinned commit:** `a15ec2d68d51dbe6a39d1da688ec7a3f642d846c`

## Purpose

Create a fast, local and auditable PDF preprocessing layer for research reports, newsletters, papers, historical datasets and framework source documents.

The layer converts native-text PDFs into clean Markdown and routes scanned, image-based or mixed pages toward later OCR or vision processing.

It does not interpret markets, create framework truth or produce portfolio action.

## Integration model

```text
PDF input
-> validate PDF magic and bounded size
-> build pinned pdf-inspector source in GitHub Actions
-> classify document and layout
-> extract native text to page-marked Markdown
-> record source and output SHA-256 hashes
-> flag OCR or vision requirements
-> upload result as a short-lived Actions artifact
```

## Why the upstream source is sufficient

The integration does not require an OpenAI API key, paid service, browser session or local computer.

GitHub Actions fetches one immutable upstream commit, builds the Rust command-line tools and runs them inside the repository workflow.

The upstream repository is not copied into the framework repository. Only the pinned commit reference and the framework wrapper are retained.

## Outputs

Each run produces:

```text
detection.json
manifest.json
document.md, when extractable native text exists
```

The manifest records:

- source filename, bytes and SHA-256;
- upstream repository and commit;
- detector and extractor exit codes;
- PDF type and page count when exposed by upstream;
- pages requiring OCR;
- pages with tables or columns when exposed by upstream;
- encoding and layout warnings;
- output file hashes;
- zero-authority flags.

## Storage policy

Raw PDF input is not committed automatically.

Generated outputs are uploaded as GitHub Actions artifacts with 14-day retention. Permanent archive promotion requires a separate deliberate write, source lineage and normal storage-health rules.

This preserves the Free-plan storage policy:

```text
bulk binary in Git: no
compact metadata in Git: allowed
short-lived processing artifacts: allowed
```

## Authority

The ingestion layer may:

- classify a PDF;
- extract native text;
- preserve page markers;
- expose tables and layout metadata;
- flag missing OCR or visual interpretation;
- generate hashes and receipts.

It may not:

- claim that extracted text is semantically complete;
- interpret charts or diagrams;
- infer missing text;
- perform OCR silently;
- change framework state;
- change model weights;
- promote canonical learning;
- create portfolio action.

## Failure handling

```text
invalid PDF magic -> BLOCKED
input over 25 MiB -> BLOCKED
upstream detector failure -> BLOCKED
native text extracted with no warnings -> READY
partial text, mixed pages or encoding issues -> DEGRADED
scanned or image-based PDF -> DEGRADED and OCR/vision required
```

A DEGRADED result is usable as partial evidence only. The original PDF remains the primary source.

## Operational access

The workflow can process:

1. a PDF path already present in the private repository;
2. a public HTTPS PDF URL;
3. an internal deterministic smoke-test PDF when no input is supplied.

Future agents can invoke the workflow without changing its authority or adding API cost.

## Promotion path

```text
IMPLEMENTED
-> CI real-parser smoke pass
-> merged shadow infrastructure
-> first real framework PDF readback
-> quality comparison against current PDF extraction path
-> optional expansion to selective OCR or vision routing
```

No automatic replacement of existing PDF handling is authorized at implementation time.
