from pydantic import BaseModel, Field


class DocumentUpsertRequest(BaseModel):
    text: str = Field(min_length=1)


class DocumentResponse(BaseModel):
    id: str
    text: str
    version: int


class DocumentDeleteResponse(BaseModel):
    success: bool


class ReplaceRange(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)


class ReplaceTarget(BaseModel):
    text: str | None = None
    occurrence: int | None = Field(default=None, ge=1)
    range: ReplaceRange | None = None


class ReplaceChange(BaseModel):
    operation: str = "replace"
    target: ReplaceTarget
    replacement: str


class DocumentPatchRequest(BaseModel):
    changes: list[ReplaceChange] = Field(min_length=1)


class SearchMatch(BaseModel):
    context: str
    start: int
    end: int


class SearchResult(BaseModel):
    id: str
    version: int
    matches: list[SearchMatch]


class SearchResponse(BaseModel):
    q: str
    total: int
    results: list[SearchResult]