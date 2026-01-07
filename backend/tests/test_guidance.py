"""Tests for guidance endpoints and logic."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestGuidanceCRUD:
    """Test guidance CRUD operations."""

    def test_create_guidance_success(self, client: TestClient, sample_folder_data):
        """Test creating a guidance record successfully."""
        # Create folder first
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Create guidance
        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
            "guidance_low": 94000000000,  # $94B
            "guidance_high": 96000000000,  # $96B
            "notes": "Q1 guidance provided during Q4 earnings",
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 201
        data = response.json()

        assert data["ticker"] == "AAPL"
        assert data["period"] == "2025-Q1"
        assert data["metric"] == "REVENUE"
        assert data["guidance_period"] == "2024-Q4"
        assert float(data["guidance_low"]) == 94000000000
        assert float(data["guidance_high"]) == 96000000000
        assert data["notes"] == "Q1 guidance provided during Q4 earnings"

    def test_create_guidance_point_estimate(self, client: TestClient, sample_folder_data):
        """Test creating guidance with point estimate."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025",
            "metric": "EPS",
            "guidance_period": "2024-Q4",
            "guidance_point": 9.50,  # Point estimate instead of range
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 201
        data = response.json()

        assert data["guidance_low"] is None
        assert data["guidance_high"] is None
        assert float(data["guidance_point"]) == 9.50

    def test_create_guidance_with_actual(self, client: TestClient, sample_folder_data):
        """Test creating guidance with actual result."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2024-Q4",
            "metric": "REVENUE",
            "guidance_period": "2024-Q3",
            "guidance_low": 90000000000,
            "guidance_high": 94000000000,
            "actual_result": 96000000000,  # Beat the high end
            "notes": "Beat guidance",
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 201
        data = response.json()

        assert float(data["actual_result"]) == 96000000000
        # Check vs_guidance_midpoint calculation
        midpoint = (90000000000 + 94000000000) / 2
        expected_vs = ((96000000000 - midpoint) / midpoint) * 100
        assert abs(float(data["vs_guidance_midpoint"]) - expected_vs) < 0.01

    def test_create_guidance_wrong_ticker(self, client: TestClient, sample_folder_data):
        """Test that ticker must belong to folder."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "MSFT",  # Wrong ticker
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 400
        assert "does not belong to folder" in response.json()["detail"]

    def test_list_guidance_by_folder(self, client: TestClient, sample_folder_data):
        """Test listing guidance for a folder."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Create multiple guidance records
        for period in ["2025-Q1", "2025-Q2", "2025-Q3"]:
            guidance_data = {
                "folder_id": folder_id,
                "ticker": "AAPL",
                "period": period,
                "metric": "REVENUE",
                "guidance_period": "2024-Q4",
                "guidance_point": 95000000000,
            }
            client.post("/api/guidance", json=guidance_data)

        # List guidance
        response = client.get(f"/api/folders/{folder_id}/guidance")
        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3
        assert len(data["guidance"]) == 3

    def test_filter_guidance_by_ticker(self, client: TestClient, sample_pair_folder_data):
        """Test filtering guidance by ticker in pair folder."""
        folder_response = client.post("/api/folders", json=sample_pair_folder_data)
        folder_id = folder_response.json()["id"]

        # Create guidance for both tickers
        for ticker in ["AAPL", "MSFT"]:
            guidance_data = {
                "folder_id": folder_id,
                "ticker": ticker,
                "period": "2025-Q1",
                "metric": "REVENUE",
                "guidance_period": "2024-Q4",
                "guidance_point": 95000000000,
            }
            client.post("/api/guidance", json=guidance_data)

        # Filter by AAPL
        response = client.get(f"/api/folders/{folder_id}/guidance?ticker=AAPL")
        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert data["guidance"][0]["ticker"] == "AAPL"

    def test_update_guidance(self, client: TestClient, sample_folder_data):
        """Test updating guidance record."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Create guidance
        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
            "guidance_low": 90000000000,
            "guidance_high": 94000000000,
        }
        create_response = client.post("/api/guidance", json=guidance_data)
        guidance_id = create_response.json()["id"]

        # Update with actual result
        update_data = {
            "actual_result": 96000000000,
            "notes": "Beat high end of guidance",
        }
        response = client.put(f"/api/guidance/{guidance_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()

        assert float(data["actual_result"]) == 96000000000
        assert data["notes"] == "Beat high end of guidance"
        assert data["vs_guidance_midpoint"] is not None

    def test_delete_guidance(self, client: TestClient, sample_folder_data):
        """Test deleting guidance record."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Create guidance
        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
            "guidance_point": 95000000000,
        }
        create_response = client.post("/api/guidance", json=guidance_data)
        guidance_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/api/guidance/{guidance_id}")
        assert response.status_code == 204

        # Verify deletion
        list_response = client.get(f"/api/folders/{folder_id}/guidance")
        assert list_response.json()["total"] == 0


@pytest.mark.unit
class TestGuidanceCalculations:
    """Test guidance calculations."""

    def test_midpoint_calculation(self, client: TestClient, sample_folder_data):
        """Test guidance midpoint calculation."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
            "guidance_low": 90000000000,
            "guidance_high": 100000000000,
        }

        response = client.post("/api/guidance", json=guidance_data)
        data = response.json()

        # Midpoint should be 95B
        expected_midpoint = 95000000000
        assert abs(float(data["guidance_midpoint"]) - expected_midpoint) < 1

    def test_vs_guidance_calculation_beat(self, client: TestClient, sample_folder_data):
        """Test vs guidance percentage when beating."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
            "guidance_low": 90000000000,
            "guidance_high": 94000000000,
            "actual_result": 95000000000,  # Beat
        }

        response = client.post("/api/guidance", json=guidance_data)
        data = response.json()

        # Midpoint is 92B, actual is 95B
        # (95 - 92) / 92 * 100 = 3.26%
        midpoint = 92000000000
        expected_vs = ((95000000000 - midpoint) / midpoint) * 100
        assert abs(float(data["vs_guidance_midpoint"]) - expected_vs) < 0.01

    def test_vs_guidance_calculation_miss(self, client: TestClient, sample_folder_data):
        """Test vs guidance percentage when missing."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
            "guidance_low": 90000000000,
            "guidance_high": 94000000000,
            "actual_result": 89000000000,  # Missed low end
        }

        response = client.post("/api/guidance", json=guidance_data)
        data = response.json()

        # Should be negative
        assert float(data["vs_guidance_midpoint"]) < 0

    def test_no_vs_guidance_without_actual(self, client: TestClient, sample_folder_data):
        """Test that vs_guidance is null without actual result."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
            "guidance_low": 90000000000,
            "guidance_high": 94000000000,
            # No actual_result
        }

        response = client.post("/api/guidance", json=guidance_data)
        data = response.json()

        assert data["vs_guidance_midpoint"] is None

    def test_point_guidance_vs_actual(self, client: TestClient, sample_folder_data):
        """Test vs guidance with point estimate."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025",
            "metric": "EPS",
            "guidance_period": "2024-Q4",
            "guidance_point": 9.00,
            "actual_result": 9.50,
        }

        response = client.post("/api/guidance", json=guidance_data)
        data = response.json()

        # (9.50 - 9.00) / 9.00 * 100 = 5.56%
        expected_vs = ((9.50 - 9.00) / 9.00) * 100
        assert abs(float(data["vs_guidance_midpoint"]) - expected_vs) < 0.01


@pytest.mark.unit
class TestGuidanceMetrics:
    """Test different guidance metric types."""

    def test_eps_guidance(self, client: TestClient, sample_folder_data):
        """Test EPS guidance."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025",
            "metric": "EPS",
            "guidance_period": "2024-Q4",
            "guidance_low": 8.50,
            "guidance_high": 9.00,
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 201
        assert response.json()["metric"] == "EPS"

    def test_ebitda_guidance(self, client: TestClient, sample_folder_data):
        """Test EBITDA guidance."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "EBITDA",
            "guidance_period": "2024-Q4",
            "guidance_low": 30000000000,
            "guidance_high": 32000000000,
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 201
        assert response.json()["metric"] == "EBITDA"

    def test_fcf_guidance(self, client: TestClient, sample_folder_data):
        """Test FCF guidance."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "FCF",
            "guidance_period": "2024-Q4",
            "guidance_point": 25000000000,
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 201
        assert response.json()["metric"] == "FCF"

    def test_other_guidance(self, client: TestClient, sample_folder_data):
        """Test OTHER metric type."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        guidance_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period": "2025",
            "metric": "OTHER",
            "guidance_period": "2024-Q4",
            "guidance_point": 150,  # e.g., store count
            "notes": "New store openings",
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 201
        assert response.json()["metric"] == "OTHER"
