from dataclasses import dataclass

from app.core.errors import DocumentNotFoundError, InvalidChangeError, InvalidRequestError, VersionConflictError
from app.stores.inverted_index import InvertedIndex
from app.schemas.documents import SearchMatch, SearchResponse, SearchResult


@dataclass
class DocumentRecord:
    id: str
    text: str
    version: int
    index: InvertedIndex

    @property
    def etag(self) -> str:
        return f"\"v{self.version}\""


class DocumentStore:
    def __init__(self) -> None:
        self._docs: dict[str, DocumentRecord] = {}

    def put_document(self, doc_id: str, text: str) -> DocumentRecord:
        existing = self._docs.get(doc_id)
        version = existing.version + 1 if existing else 1
        record = DocumentRecord(id=doc_id, text=text, version=version, index=InvertedIndex(text))
        self._docs[doc_id] = record
        return record

    def get_document(self, doc_id: str) -> DocumentRecord:
        record = self._docs.get(doc_id)
        if record is None:
            raise DocumentNotFoundError(doc_id=doc_id)
        return record

    def delete_document(self, doc_id: str) -> None:
        self.get_document(doc_id)
        del self._docs[doc_id]

    def patch_document(self, doc_id: str, changes: list[dict], if_match: str | None) -> DocumentRecord:
        record = self.get_document(doc_id)
        if if_match is not None and if_match != record.etag:
            raise VersionConflictError(doc_id=doc_id, version=record.version)

        text = record.text
        for change in changes:
            if change.get("operation") != "replace":
                raise InvalidChangeError(doc_id=doc_id, change="operation must be replace")
            target = change.get("target") or {}
            replacement = change.get("replacement")
            if replacement is None:
                raise InvalidRequestError(message="replacement is required")

            target_text = target.get("text")
            occurrence = target.get("occurrence")
            target_range = target.get("range")

            if target_text is not None:
                if not target_text:
                    raise InvalidChangeError(doc_id=doc_id, change="target.text cannot be empty")
                index = self._find_occurrence(text, target_text, occurrence or 1)
                if index < 0:
                    raise InvalidChangeError(doc_id=doc_id, change=f"text not found: {target_text}")
                text = text[:index] + replacement + text[index + len(target_text) :]
            elif target_range is not None:
                start = target_range.get("start")
                end = target_range.get("end")
                if start is None or end is None or start < 0 or end < start or end > len(text):
                    raise InvalidChangeError(doc_id=doc_id, change=f"invalid range: {target_range}")
                text = text[:start] + replacement + text[end:]
            else:
                raise InvalidChangeError(doc_id=doc_id, change="target.text or target.range required")

        return self.put_document(doc_id, text)

    def search_all(self, query: str, limit: int, offset: int) -> SearchResponse:
        results: list[SearchResult] = []
        for record in self._docs.values():
            matches = self._matches_for_record(record, query)
            if matches:
                results.append(SearchResult(id=record.id, version=record.version, matches=matches))

        paged = results[offset : offset + limit]
        return SearchResponse(q=query, total=len(results), results=paged)

    def search_document(self, doc_id: str, query: str, limit: int, offset: int) -> SearchResponse:
        record = self.get_document(doc_id)
        matches = self._matches_for_record(record, query)
        results = [SearchResult(id=record.id, version=record.version, matches=matches)] if matches else []
        paged = results[offset : offset + limit]
        return SearchResponse(q=query, total=len(results), results=paged)

    @staticmethod
    def _find_occurrence(text: str, needle: str, occurrence: int) -> int:
        if occurrence < 1:
            return -1
        start = 0
        count = 0
        while True:
            idx = text.find(needle, start)
            if idx < 0:
                return -1
            count += 1
            if count == occurrence:
                return idx
            start = idx + len(needle)

    @staticmethod
    def _snippet(text: str, start: int, end: int, window: int = 40) -> str:
        left = max(0, start - window)
        right = min(len(text), end + window)
        return text[left:right]

    def _matches_for_record(self, record: DocumentRecord, query: str) -> list[SearchMatch]:
        spans = record.index.phrase_matches(query)
        return [
            SearchMatch(
                context=self._snippet(record.text, start, end),
                start=start,
                end=end,
            )
            for start, end in spans
        ]
