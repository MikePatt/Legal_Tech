from app.schemas.documents import DocumentUpsertRequest
from app.services import document_service


def _reset_store() -> None:
    document_service.store._docs.clear()


def test_phrase_search_across_documents() -> None:
    _reset_store()
    document_service.put_document("a", DocumentUpsertRequest(text="Master service agreement for software."))
    document_service.put_document("b", DocumentUpsertRequest(text="This agreement governs delivery terms."))
    document_service.put_document("c", DocumentUpsertRequest(text="No matching phrase here."))

    response = document_service.search_all_documents("service agreement", limit=10, offset=0)
    assert response.total == 1
    assert response.results[0].id == "a"
    assert response.results[0].matches[0].context


def test_search_pagination() -> None:
    _reset_store()
    document_service.put_document("a", DocumentUpsertRequest(text="contract contract"))
    document_service.put_document("b", DocumentUpsertRequest(text="contract language"))
    document_service.put_document("c", DocumentUpsertRequest(text="contract terms"))

    response = document_service.search_all_documents("contract", limit=1, offset=1)
    assert response.total == 3
    assert len(response.results) == 1
