from app.schemas.documents import DocumentPatchRequest, DocumentUpsertRequest, ReplaceChange, ReplaceRange, ReplaceTarget
from app.services import document_service


def _reset_store() -> None:
    document_service.store._docs.clear()


def test_occurrence_replace_changes_nth_match() -> None:
    _reset_store()
    document_service.put_document("d1", DocumentUpsertRequest(text="alpha beta alpha beta"))
    request = DocumentPatchRequest(
        changes=[
            ReplaceChange(
                operation="replace",
                target=ReplaceTarget(text="alpha", occurrence=2),
                replacement="omega",
            )
        ]
    )
    updated, _etag = document_service.patch_document("d1", request, None)
    assert updated.text == "alpha beta omega beta"


def test_range_replace_updates_substring() -> None:
    _reset_store()
    document_service.put_document("d2", DocumentUpsertRequest(text="hello world"))
    request = DocumentPatchRequest(
        changes=[
            ReplaceChange(
                operation="replace",
                target=ReplaceTarget(range=ReplaceRange(start=6, end=11)),
                replacement="legal",
            )
        ]
    )
    updated, _etag = document_service.patch_document("d2", request, None)
    assert updated.text == "hello legal"
