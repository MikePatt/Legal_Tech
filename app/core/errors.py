from fastapi import HTTPException, status


class ApiError(HTTPException):
    def __init__(self, *, status_code: int, code: int, error: str) -> None:
        super().__init__(
            status_code=status_code,
            detail={
                "error": error,
                "code": code,
            },
        )

class DocumentNotFoundError(ApiError):
    def __init__(self, *, doc_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=4040,
            error=f"Document {doc_id} not found",
        )


class InvalidChangeError(ApiError):
    def __init__(self, *, doc_id: str, change: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=4000,
            error=f"Invalid change: {change} for document {doc_id}",
        )


class VersionConflictError(ApiError):
    def __init__(self, *, doc_id: str, version: int) -> None:
        super().__init__(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            code=4120,
            error=f"Version conflict for document {doc_id}: {version}",
        )


class InvalidRequestError(ApiError):
    def __init__(self, *, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=4000,
            error=message,
        )