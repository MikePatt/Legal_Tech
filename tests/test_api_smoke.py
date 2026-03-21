from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_put_patch_and_search_flow() -> None:
    put_response = client.put("/documents/doc-1", json={"text": "the old contract term is old"})
    assert put_response.status_code == 200
    etag = put_response.headers.get("etag")
    assert etag

    patch_response = client.patch(
        "/documents/doc-1",
        headers={"If-Match": etag},
        json={
            "changes": [
                {
                    "operation": "replace",
                    "target": {"text": "old", "occurrence": 2},
                    "replacement": "new",
                }
            ]
        },
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["text"] == "the old contract term is new"

    search_response = client.get("/documents/doc-1/search", params={"q": "contract term"})
    assert search_response.status_code == 200
    body = search_response.json()
    assert body["total"] == 1
    assert body["results"][0]["id"] == "doc-1"
