"""API contracts, pagination and invalid-input behavior."""

import pytest
from fastapi.testclient import TestClient


def test_create_and_paginate(client: TestClient) -> None:
    """Created records persist, and pages have stable ordering."""
    for name in ("First", "Second", "Third"):
        response = client.post("/api/v1/items/", json={"name": name})
        assert response.status_code == 201
    response = client.get("/api/v1/items/", params={"limit": 1, "offset": 1})
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Second"]


@pytest.mark.parametrize("name", ["", "x" * 121])
def test_invalid_name_returns_validation_error(client: TestClient, name: str) -> None:
    """Invalid input is rejected as a client error before persistence."""
    assert client.post("/api/v1/items/", json={"name": name}).status_code == 422
    assert client.get("/api/v1/items/").json() == []


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
def test_pagination_bounds(client: TestClient, query: str) -> None:
    """Clients cannot request unbounded pages or negative offsets."""
    assert client.get(f"/api/v1/items/?{query}").status_code == 422
