from app.schemas import documents as document_schemas
from app.stores.doc_store import DocumentStore

store = DocumentStore()


def put_document(doc_id: str, request: document_schemas.DocumentUpsertRequest) -> tuple[document_schemas.DocumentResponse, str]:
    record = store.put_document(doc_id, request.text)
    return document_schemas.DocumentResponse(id=record.id, text=record.text, version=record.version), record.etag


def patch_document(
    doc_id: str, request: document_schemas.DocumentPatchRequest, if_match: str | None
) -> tuple[document_schemas.DocumentResponse, str]:
    changes = [c.model_dump() if hasattr(c, "model_dump") else c.dict() for c in request.changes]
    record = store.patch_document(doc_id, changes, if_match)
    return document_schemas.DocumentResponse(id=record.id, text=record.text, version=record.version), record.etag


def get_document(doc_id: str) -> tuple[document_schemas.DocumentResponse, str]:
    record = store.get_document(doc_id)
    return document_schemas.DocumentResponse(id=record.id, text=record.text, version=record.version), record.etag


def delete_document(doc_id: str) -> document_schemas.DocumentDeleteResponse:
    store.delete_document(doc_id)
    return document_schemas.DocumentDeleteResponse(success=True)


def search_all_documents(q: str, limit: int, offset: int) -> document_schemas.SearchResponse:
    return store.search_all(q, limit, offset)


def search_document(doc_id: str, q: str, limit: int, offset: int) -> tuple[document_schemas.SearchResponse, str]:
    record = store.get_document(doc_id)
    response = store.search_document(doc_id, q, limit, offset)
    return response, record.etag