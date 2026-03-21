from fastapi import APIRouter, Header, Query, Response, status

from app.schemas import documents as document_schemas
from app.services import document_service

router = APIRouter()


@router.put("/documents/{doc_id}", response_model=document_schemas.DocumentResponse, status_code=status.HTTP_200_OK)
def put_document_route(doc_id: str, request: document_schemas.DocumentUpsertRequest, response: Response):
    result, etag = document_service.put_document(doc_id, request)
    response.headers["ETag"] = etag
    return result


@router.patch("/documents/{doc_id}", response_model=document_schemas.DocumentResponse, status_code=status.HTTP_200_OK)
def patch_document_route(
    doc_id: str,
    request: document_schemas.DocumentPatchRequest,
    response: Response,
    if_match: str | None = Header(default=None, alias="If-Match"),
):
    result, etag = document_service.patch_document(doc_id, request, if_match)
    response.headers["ETag"] = etag
    return result


@router.get("/documents/search", response_model=document_schemas.SearchResponse, status_code=status.HTTP_200_OK)
def search_documents_route(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return document_service.search_all_documents(q=q, limit=limit, offset=offset)


@router.get("/documents/{doc_id}/search", response_model=document_schemas.SearchResponse, status_code=status.HTTP_200_OK)
def search_document_route(
    doc_id: str,
    response: Response,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    result, etag = document_service.search_document(doc_id=doc_id, q=q, limit=limit, offset=offset)
    response.headers["ETag"] = etag
    return result


@router.get("/documents/{doc_id}", response_model=document_schemas.DocumentResponse, status_code=status.HTTP_200_OK)
def get_document_route(doc_id: str, response: Response):
    result, etag = document_service.get_document(doc_id)
    response.headers["ETag"] = etag
    return result


@router.delete("/documents/{doc_id}", response_model=document_schemas.DocumentDeleteResponse, status_code=status.HTTP_200_OK)
def delete_document_route(doc_id: str):
    return document_service.delete_document(doc_id)
