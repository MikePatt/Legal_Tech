# Legal Tech Redlining Service

FastAPI service that supports document updates and search across document content.

## Features

- `PUT /documents/{id}` stores a document body and increments version.
- `PATCH /documents/{id}` applies one or more replace operations in order.
- `GET /documents/search` searches all documents and returns snippet context.
- `GET /documents/{id}/search` searches within a single document.
- ETag based optimistic concurrency with `If-Match` support on `PATCH`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Run

```bash
uvicorn main:app --reload
```

## API Usage

### Create/replace a document

```bash
curl -X PUT "http://127.0.0.1:8000/documents/msa-001" \
  -H "Content-Type: application/json" \
  -d '{"text":"This Master Service Agreement governs delivery obligations."}'
```

### Patch by occurrence

```bash
curl -X PATCH "http://127.0.0.1:8000/documents/msa-001" \
  -H "Content-Type: application/json" \
  -H 'If-Match: "v1"' \
  -d '{"changes":[{"operation":"replace","target":{"text":"delivery","occurrence":1},"replacement":"implementation"}]}'
```

### Search all documents

```bash
curl "http://127.0.0.1:8000/documents/search?q=agreement&limit=10&offset=0"
```

### Search one document

```bash
curl "http://127.0.0.1:8000/documents/msa-001/search?q=service%20agreement"
```

Additional examples are in `examples/`.

## Project layout

```
main.py              # FastAPI app + exception handlers
app/
  api/routes.py      # HTTP routes
  core/errors.py     # API error types
  schemas/           # Pydantic models
  services/          # document_service (orchestration + shared store)
  stores/            # DocumentStore + inverted_index
tests/
examples/
```

## Tests

```bash
pytest
```

## Performance Notes

- Search uses an in-memory inverted index (`token -> token positions`) built per document.
- Query processing tokenizes query text and performs phrase verification using adjacent token positions.
- Replace operations are linear in document size for occurrence and range replacement.
- `tests/test_large_file.py` exercises indexing and search on a ~10MB synthetic document.

## API Design Rationale

- Write operations (`PUT`, `PATCH`) are separated from read operations (`GET search`).
- `PATCH` supports bulk changes by accepting an array of `changes`.
- ETag/If-Match prevents stale updates by returning `412` on version mismatch.
