import time

from app.schemas.documents import DocumentUpsertRequest
from app.services import document_service


def _reset_store() -> None:
    document_service.store._docs.clear()


def test_large_document_indexing_and_search_perf() -> None:
    _reset_store()
    token = "contractclause "
    text = token * 700_000  # ~10MB

    start = time.perf_counter()
    document_service.put_document("big", DocumentUpsertRequest(text=text))
    indexing_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    result = document_service.search_all_documents("contractclause", limit=1, offset=0)
    search_elapsed = time.perf_counter() - start

    assert result.total == 1
    assert indexing_elapsed < 8.0
    assert search_elapsed < 8.0
