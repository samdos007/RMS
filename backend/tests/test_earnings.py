"""Tests for earnings endpoints and logic."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.unit
class TestEarningsCRUD:
    """Test earnings CRUD operations."""

    def test_create_earnings_success(self, client: TestClient, sample_folder_data):
        """Test creating an earnings record successfully."""
        # Create folder first
        folder_response = client.post("/api/folders", json=sample_folder_data)
        assert folder_response.status_code == 201
        folder_id = folder_response.json()["id"]

        # Create earnings
        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "period": "2024-Q4",
            "fiscal_quarter": "2024-Q4",
            "estimate_eps": 2.35,
            "actual_eps": 2.48,
            "estimate_rev": 95000000000,  # $95B in raw format
            "actual_rev": 96000000000,  # $96B
            "notes": "Beat on both metrics",
        }

        response = client.post("/api/earnings", json=earnings_data)
        assert response.status_code == 201
        data = response.json()

        assert data["ticker"] == "AAPL"
        assert data["period_type"] == "QUARTERLY"
        assert data["period"] == "2024-Q4"
        assert data["fiscal_quarter"] == "2024-Q4"
        assert float(data["estimate_eps"]) == 2.35
        assert float(data["actual_eps"]) == 2.48
        assert data["notes"] == "Beat on both metrics"

        # Check surprise calculations
        assert data["eps_surprise_pct"] is not None
        eps_surprise = float(data["eps_surprise_pct"])
        expected_surprise = ((2.48 - 2.35) / 2.35) * 100
        assert abs(eps_surprise - expected_surprise) < 0.01

    def test_create_earnings_annual(self, client: TestClient, sample_folder_data):
        """Test creating annual earnings record."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "ANNUAL",
            "period": "2024",
            "fiscal_quarter": "2024",
            "estimate_eps": 9.20,
            "actual_eps": 9.50,
        }

        response = client.post("/api/earnings", json=earnings_data)
        assert response.status_code == 201
        assert response.json()["period_type"] == "ANNUAL"

    def test_create_earnings_missing_period(self, client: TestClient, sample_folder_data):
        """Test that fiscal_quarter is required."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            # Missing fiscal_quarter
        }

        response = client.post("/api/earnings", json=earnings_data)
        assert response.status_code == 422

    def test_create_earnings_wrong_ticker(self, client: TestClient, sample_folder_data):
        """Test that ticker must belong to folder."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "MSFT",  # Wrong ticker
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
        }

        response = client.post("/api/earnings", json=earnings_data)
        assert response.status_code == 400
        assert "does not belong to folder" in response.json()["detail"]

    def test_create_earnings_duplicate(self, client: TestClient, sample_folder_data):
        """Test that duplicate earnings are prevented."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
        }

        # Create first earnings
        response1 = client.post("/api/earnings", json=earnings_data)
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = client.post("/api/earnings", json=earnings_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    def test_list_earnings_by_folder(self, client: TestClient, sample_folder_data):
        """Test listing earnings for a folder."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Create multiple earnings
        for quarter in ["2024-Q1", "2024-Q2", "2024-Q3"]:
            earnings_data = {
                "folder_id": folder_id,
                "ticker": "AAPL",
                "period_type": "QUARTERLY",
                "fiscal_quarter": quarter,
                "period": quarter,
            }
            client.post("/api/earnings", json=earnings_data)

        # List earnings
        response = client.get(f"/api/folders/{folder_id}/earnings")
        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3
        assert len(data["earnings"]) == 3

    def test_update_earnings(self, client: TestClient, sample_folder_data):
        """Test updating earnings record."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Create earnings
        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "estimate_eps": 2.35,
        }
        create_response = client.post("/api/earnings", json=earnings_data)
        earnings_id = create_response.json()["id"]

        # Update with actual
        update_data = {
            "actual_eps": 2.48,
            "notes": "Beat estimates",
        }
        response = client.put(f"/api/earnings/{earnings_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()

        assert float(data["actual_eps"]) == 2.48
        assert data["notes"] == "Beat estimates"
        assert data["eps_surprise_pct"] is not None

    def test_delete_earnings(self, client: TestClient, sample_folder_data):
        """Test deleting earnings record."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Create earnings
        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
        }
        create_response = client.post("/api/earnings", json=earnings_data)
        earnings_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/api/earnings/{earnings_id}")
        assert response.status_code == 204

        # Verify deletion
        list_response = client.get(f"/api/folders/{folder_id}/earnings")
        assert list_response.json()["total"] == 0


@pytest.mark.unit
class TestEarningsCalculations:
    """Test earnings surprise calculations."""

    def test_eps_surprise_calculation(self, client: TestClient, sample_folder_data):
        """Test EPS surprise percentage calculation."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "estimate_eps": 2.00,
            "actual_eps": 2.10,
        }

        response = client.post("/api/earnings", json=earnings_data)
        data = response.json()

        # (2.10 - 2.00) / 2.00 * 100 = 5.0%
        assert abs(float(data["eps_surprise_pct"]) - 5.0) < 0.01
        assert abs(float(data["eps_surprise"]) - 0.10) < 0.01

    def test_revenue_surprise_calculation(self, client: TestClient, sample_folder_data):
        """Test revenue surprise percentage calculation."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "estimate_rev": 90000000000,  # $90B
            "actual_rev": 94500000000,  # $94.5B
        }

        response = client.post("/api/earnings", json=earnings_data)
        data = response.json()

        # (94.5 - 90) / 90 * 100 = 5.0%
        expected_pct = ((94.5 - 90) / 90) * 100
        assert abs(float(data["rev_surprise_pct"]) - expected_pct) < 0.01

    def test_ebitda_surprise_calculation(self, client: TestClient, sample_folder_data):
        """Test EBITDA surprise percentage calculation."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "estimate_ebitda": 30000000000,  # $30B
            "actual_ebitda": 31500000000,  # $31.5B
        }

        response = client.post("/api/earnings", json=earnings_data)
        data = response.json()

        # (31.5 - 30) / 30 * 100 = 5.0%
        expected_pct = ((31.5 - 30) / 30) * 100
        assert abs(float(data["ebitda_surprise_pct"]) - expected_pct) < 0.01

    def test_fcf_surprise_calculation(self, client: TestClient, sample_folder_data):
        """Test FCF surprise percentage calculation."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "estimate_fcf": 25000000000,  # $25B
            "actual_fcf": 27000000000,  # $27B
        }

        response = client.post("/api/earnings", json=earnings_data)
        data = response.json()

        # (27 - 25) / 25 * 100 = 8.0%
        expected_pct = ((27 - 25) / 25) * 100
        assert abs(float(data["fcf_surprise_pct"]) - expected_pct) < 0.01

    def test_negative_surprise(self, client: TestClient, sample_folder_data):
        """Test negative surprise (miss)."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "estimate_eps": 2.50,
            "actual_eps": 2.30,  # Missed
        }

        response = client.post("/api/earnings", json=earnings_data)
        data = response.json()

        # (2.30 - 2.50) / 2.50 * 100 = -8.0%
        expected_pct = ((2.30 - 2.50) / 2.50) * 100
        assert float(data["eps_surprise_pct"]) < 0
        assert abs(float(data["eps_surprise_pct"]) - expected_pct) < 0.01

    def test_no_surprise_when_missing_data(self, client: TestClient, sample_folder_data):
        """Test that surprise is null when estimate or actual is missing."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Only estimate, no actual
        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "estimate_eps": 2.35,
        }

        response = client.post("/api/earnings", json=earnings_data)
        data = response.json()

        assert data["eps_surprise"] is None
        assert data["eps_surprise_pct"] is None


@pytest.mark.unit
class TestEarningsPairFolder:
    """Test earnings with pair folders."""

    def test_create_earnings_for_pair_folder(self, client: TestClient, sample_pair_folder_data):
        """Test creating earnings for both tickers in a pair folder."""
        folder_response = client.post("/api/folders", json=sample_pair_folder_data)
        folder_id = folder_response.json()["id"]

        # Create earnings for first ticker
        earnings_data_aapl = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "actual_eps": 2.48,
        }
        response1 = client.post("/api/earnings", json=earnings_data_aapl)
        assert response1.status_code == 201

        # Create earnings for second ticker
        earnings_data_msft = {
            "folder_id": folder_id,
            "ticker": "MSFT",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
            "actual_eps": 2.93,
        }
        response2 = client.post("/api/earnings", json=earnings_data_msft)
        assert response2.status_code == 201

        # List all earnings
        list_response = client.get(f"/api/folders/{folder_id}/earnings")
        assert list_response.json()["total"] == 2

        # Filter by ticker
        aapl_response = client.get(f"/api/folders/{folder_id}/earnings?ticker=AAPL")
        assert aapl_response.json()["total"] == 1
        assert aapl_response.json()["earnings"][0]["ticker"] == "AAPL"
