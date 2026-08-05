# AnyDoc Agent Document Normalization v1

**Dato:** 2026-08-05  
**Status:** OPERATIONAL_AGENT_UTILITY  
**Område:** mixed document ingestion / Markdown normalization / agent context preparation  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Related folders:** `scripts/document_ingestion/`, `tests/document_ingestion/`, `scripts/pdf_ingestion/`, `research/pdf_ingestion/`  
**Depends on:** `AGENTS.md`, `.agents/skills/archive-governance/SKILL.md`, `research/pdf_ingestion/PDF_INSPECTOR_INGESTION_ARCHITECTURE_v1.md`

## 1. Decision

AnyDoc is adopted as a bounded document-normalization utility for repository-aware agents.

It is not a new framework engine, shadow layer, research package owner or truth source.

It extends the existing document intake capability from PDF-only preprocessing to mixed office and publishing formats without replacing the active PDF Inspector route.

## 2. Repeated workflow gap

Observed failure mode:

```text
Agents receive Word, PowerPoint, Excel, OpenDocument, RTF, EPUB or CSV sources,
but the repository only has a specialized PDF preprocessing owner.
```

Repeated task frequency:

```text
HIGH enough to justify one reusable utility because framework research,
archive recovery and external audits repeatedly arrive in mixed file formats.
```

Why existing skills cannot cover it alone:

```text
archive-governance can classify and place material,
but it does not currently normalize non-PDF binary documents into searchable Markdown.
```

## 3. Upstream pin

```yaml
repository: https://github.com/firecrawl/anydoc
npm_package: "@firecrawl/anydoc"
pinned_version: "0.1.3"
node_requirement: ">=20"
license: MIT
```

The wrapper invokes the pinned package through:

```text
npx -y @firecrawl/anydoc@0.1.3 <input> -o <output>
```

A preinstalled explicit binary may be supplied for deterministic testing or controlled execution.

## 4. Supported routing

Primary AnyDoc route:

```text
.doc .docx .docm
.ppt .pps .pot .pptx .pptm .ppsx .ppsm
.xls .xlsx .xlsm .xlsb
.odt .ods .odp
.rtf .epub .csv
```

PDF precedence:

```text
.pdf
-> existing PDF Inspector route by default
-> AnyDoc only as an explicit fallback
-> fallback status remains DEGRADED because no separate layout/OCR receipt is produced
```

Scanned or image-only PDF:

```text
BLOCK or route to OCR/vision.
Never infer missing text.
```

## 5. Agent invocation

Normal mixed document:

```bash
python scripts/document_ingestion/anydoc_ingest.py \
  --input path/to/source.docx \
  --output-dir /tmp/anydoc-output
```

Extensionless or ambiguous source:

```bash
python scripts/document_ingestion/anydoc_ingest.py \
  --input path/to/source \
  --format-hint csv \
  --output-dir /tmp/anydoc-output
```

Explicit PDF fallback only when the specialized route is unavailable or a fast text-only convenience copy is intentionally requested:

```bash
python scripts/document_ingestion/anydoc_ingest.py \
  --input path/to/source.pdf \
  --allow-pdf-fallback \
  --output-dir /tmp/anydoc-output
```

## 6. Outputs

Each successful run produces:

```text
document.md
manifest.json
```

The receipt records:

- original filename, bytes and SHA-256;
- normalized format;
- pinned parser package and version;
- invocation mode and exit code;
- output SHA-256;
- PDF routing state;
- OCR and visual-interpretation boundaries;
- zero-authority fields.

The original source remains primary evidence.

## 7. Authority boundary

The utility may:

- convert supported documents into GitHub-Flavored Markdown;
- make mixed source material searchable and easier for agents to inspect;
- create source and output hashes;
- produce a bounded ingestion receipt;
- identify when the existing PDF specialist must be used.

It may not:

- declare extracted Markdown semantically complete;
- silently perform OCR;
- interpret charts, diagrams or embedded images;
- infer missing values;
- create owner truth;
- change framework state or model weights;
- promote archive material to canonical status;
- produce portfolio action.

## 8. Storage and context discipline

- Do not auto-commit raw documents or generated Markdown.
- Use temporary output directories by default.
- For large documents, write Markdown to file and read only relevant sections into agent context.
- Permanent promotion requires normal source lineage, classification, archive-governance and storage-health checks.
- The conversion receipt is not an evidence outcome row.

## 9. Validation

Deterministic wrapper coverage:

```yaml
tests: 6
cases:
  - office document success
  - PDF precedence block
  - explicit PDF fallback degradation
  - extensionless CSV format hint
  - converter failure
  - unsupported extension
```

A real upstream conversion should be smoke-tested in an environment with Node 20 and package-network access before this utility is used as a production dependency in scheduled automation.

No scheduled workflow is added by this change.

## 10. Kill or modification criteria

Modify, suspend or remove the utility if it:

- creates duplicate PDF handling instead of respecting the existing specialist owner;
- changes output incompatibly without a pinned-version update;
- loses source hashes or authority boundaries;
- adds more manual repair than direct conversion;
- silently accepts empty or failed conversions;
- causes archive inflation or automatic source promotion;
- becomes dependent on a paid hosted service for normal supported documents.

## 11. Operational effect

```yaml
new_engine_created: false
new_shadow_layer_created: false
new_skill_created: false
existing_skill_capability_extended: archive-governance
scheduled_automation_added: false
openai_api_required: false
framework_state_changed: false
portfolio_action_changed: false
canonical_promotion_added: false
```
