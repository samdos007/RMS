"""Tests for folder-specific functionality."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestFolderTickers:
    """Test folder tickers property."""

    def test_single_folder_tickers(self, client: TestClient, sample_folder_data):
        """Test that single folder returns one ticker."""
        response = client.post("/api/folders", json=sample_folder_data)
        assert response.status_code == 201
        data = response.json()

        assert "tickers" in data
        assert len(data["tickers"]) == 1
        assert data["tickers"][0] == "AAPL"

    def test_pair_folder_tickers(self, client: TestClient, sample_pair_folder_data):
        """Test that pair folder returns both tickers."""
        response = client.post("/api/folders", json=sample_pair_folder_data)
        assert response.status_code == 201
        data = response.json()

        assert "tickers" in data
        assert len(data["tickers"]) == 2
        assert "AAPL" in data["tickers"]
        assert "MSFT" in data["tickers"]

    def test_tickers_uppercase(self, client: TestClient):
        """Test that tickers are returned in uppercase."""
        folder_data = {
            "type": "SINGLE",
            "ticker_primary": "aapl",  # lowercase
            "description": "Test",
        }
        response = client.post("/api/folders", json=folder_data)
        data = response.json()

        # Should be uppercase in response
        assert data["tickers"][0] == "AAPL"

    def test_get_folder_includes_tickers(self, client: TestClient, sample_folder_data):
        """Test that GET /folders/{id} includes tickers."""
        create_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = create_response.json()["id"]

        get_response = client.get(f"/api/folders/{folder_id}")
        assert get_response.status_code == 200
        data = get_response.json()

        assert "tickers" in data
        assert data["tickers"] == ["AAPL"]

    def test_list_folders_includes_tickers(self, client: TestClient, sample_folder_data):
        """Test that GET /folders includes tickers in list."""
        client.post("/api/folders", json=sample_folder_data)

        list_response = client.get("/api/folders")
        assert list_response.status_code == 200
        data = list_response.json()

        assert data["total"] > 0
        folder = data["folders"][0]
        assert "tickers" in folder
        assert folder["tickers"] == ["AAPL"]
