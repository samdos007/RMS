"""Integration tests for cross-module functionality."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestEarningsFolderIntegration:
    """Test integration between earnings and folders."""

    def test_cannot_create_earnings_for_nonexistent_folder(self, client: TestClient):
        """Test that earnings requires valid folder."""
        earnings_data = {
            "folder_id": "nonexistent-id",
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
        }

        response = client.post("/api/earnings", json=earnings_data)
        assert response.status_code == 404

    def test_delete_folder_cascades_to_earnings(self, client: TestClient, sample_folder_data):
        """Test that deleting folder deletes its earnings."""
        # Create folder
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Create earnings
        earnings_data = {
            "folder_id": folder_id,
            "ticker": "AAPL",
            "period_type": "QUARTERLY",
            "fiscal_quarter": "2024-Q4",
        }
        client.post("/api/earnings", json=earnings_data)

        # Delete folder
        delete_response = client.delete(f"/api/folders/{folder_id}")
        assert delete_response.status_code == 204

        # Try to list earnings (folder is gone, so this should 404)
        earnings_list = client.get(f"/api/folders/{folder_id}/earnings")
        assert earnings_list.status_code == 404

    def test_ticker_validation_across_folder_types(self, client: TestClient):
        """Test ticker validation for both single and pair folders."""
        # Create single folder
        single_folder = client.post(
            "/api/folders",
            json={
                "type": "SINGLE",
                "ticker_primary": "AAPL",
            },
        )
        single_id = single_folder.json()["id"]

        # Can create earnings for AAPL
        earnings1 = client.post(
            "/api/earnings",
            json={
                "folder_id": single_id,
                "ticker": "AAPL",
                "period_type": "QUARTERLY",
                "fiscal_quarter": "2024-Q4",
            },
        )
        assert earnings1.status_code == 201

        # Cannot create earnings for MSFT
        earnings2 = client.post(
            "/api/earnings",
            json={
                "folder_id": single_id,
                "ticker": "MSFT",
                "period_type": "QUARTERLY",
                "fiscal_quarter": "2024-Q4",
            },
        )
        assert earnings2.status_code == 400

        # Create pair folder
        pair_folder = client.post(
            "/api/folders",
            json={
                "type": "PAIR",
                "ticker_primary": "AAPL",
                "ticker_secondary": "MSFT",
            },
        )
        pair_id = pair_folder.json()["id"]

        # Can create earnings for both tickers
        earnings3 = client.post(
            "/api/earnings",
            json={
                "folder_id": pair_id,
                "ticker": "AAPL",
                "period_type": "QUARTERLY",
                "fiscal_quarter": "2024-Q4",
            },
        )
        assert earnings3.status_code == 201

        earnings4 = client.post(
            "/api/earnings",
            json={
                "folder_id": pair_id,
                "ticker": "MSFT",
                "period_type": "QUARTERLY",
                "fiscal_quarter": "2024-Q4",
            },
        )
        assert earnings4.status_code == 201


@pytest.mark.integration
class TestGuidanceFolderIntegration:
    """Test integration between guidance and folders."""

    def test_cannot_create_guidance_for_nonexistent_folder(self, client: TestClient):
        """Test that guidance requires valid folder."""
        guidance_data = {
            "folder_id": "nonexistent-id",
            "ticker": "AAPL",
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 404

    def test_delete_folder_cascades_to_guidance(self, client: TestClient, sample_folder_data):
        """Test that deleting folder deletes its guidance."""
        # Create folder
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
        client.post("/api/guidance", json=guidance_data)

        # Delete folder
        delete_response = client.delete(f"/api/folders/{folder_id}")
        assert delete_response.status_code == 204

        # Try to list guidance (folder is gone, so this should 404)
        guidance_list = client.get(f"/api/folders/{folder_id}/guidance")
        assert guidance_list.status_code == 404

    def test_guidance_ticker_validation(self, client: TestClient, sample_folder_data):
        """Test that guidance validates ticker belongs to folder."""
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # Try to create guidance for wrong ticker
        guidance_data = {
            "folder_id": folder_id,
            "ticker": "MSFT",  # Folder is for AAPL
            "period": "2025-Q1",
            "metric": "REVENUE",
            "guidance_period": "2024-Q4",
            "guidance_point": 95000000000,
        }

        response = client.post("/api/guidance", json=guidance_data)
        assert response.status_code == 400
        assert "does not belong to folder" in response.json()["detail"]


@pytest.mark.integration
class TestEarningsGuidanceWorkflow:
    """Test realistic workflow combining earnings and guidance."""

    def test_complete_earnings_cycle(self, client: TestClient, sample_folder_data):
        """Test complete earnings cycle: guidance -> estimate -> actual."""
        # Create folder
        folder_response = client.post("/api/folders", json=sample_folder_data)
        folder_id = folder_response.json()["id"]

        # 1. Company provides Q1 guidance during Q4 earnings
        guidance_response = client.post(
            "/api/guidance",
            json={
                "folder_id": folder_id,
                "ticker": "AAPL",
                "period": "2025-Q1",
                "metric": "REVENUE",
                "guidance_period": "2024-Q4",
                "guidance_low": 90000000000,
                "guidance_high": 94000000000,
            },
        )
        assert guidance_response.status_code == 201

        # 2. Analysts set consensus estimates for Q1
        earnings_estimate = client.post(
            "/api/earnings",
            json={
                "folder_id": folder_id,
                "ticker": "AAPL",
                "period_type": "QUARTERLY",
                "fiscal_quarter": "2025-Q1",
                "period": "2025-Q1",
                "estimate_eps": 2.35,
                "estimate_rev": 92000000000,  # Within guidance range
            },
        )
        assert earnings_estimate.status_code == 201
        earnings_id = earnings_estimate.json()["id"]

        # 3. Q1 earnings are reported
        actual_update = client.put(
            f"/api/earnings/{earnings_id}",
            json={
                "actual_eps": 2.48,
                "actual_rev": 95000000000,  # Beat guidance
            },
        )
        assert actual_update.status_code == 200
        earnings_data = actual_update.json()

        # Verify surprise calculations
        assert earnings_data["eps_surprise_pct"] is not None
        assert earnings_data["rev_surprise_pct"] is not None
        assert float(earnings_data["eps_surprise_pct"]) > 0  # Beat
        assert float(earnings_data["rev_surprise_pct"]) > 0  # Beat

        # 4. Update guidance with actual result
        guidance_id = guidance_response.json()["id"]
        guidance_update = client.put(
            f"/api/guidance/{guidance_id}",
            json={"actual_result": 95000000000},
        )
        assert guidance_update.status_code == 200
        guidance_data = guidance_update.json()

        # Verify vs guidance calculation
        assert guidance_data["vs_guidance_midpoint"] is not None
        assert float(guidance_data["vs_guidance_midpoint"]) > 0  # Beat midpoint

    def test_pair_folder_complete_workflow(self, client: TestClient, sample_pair_folder_data):
        """Test complete workflow for pair folder with both tickers."""
        # Create pair folder
        folder_response = client.post("/api/folders", json=sample_pair_folder_data)
        folder_id = folder_response.json()["id"]

        # Create guidance for both tickers
        for ticker in ["AAPL", "MSFT"]:
            client.post(
                "/api/guidance",
                json={
                    "folder_id": folder_id,
                    "ticker": ticker,
                    "period": "2025-Q1",
                    "metric": "REVENUE",
                    "guidance_period": "2024-Q4",
                    "guidance_point": 95000000000,
                },
            )

        # Create earnings for both tickers
        for ticker in ["AAPL", "MSFT"]:
            client.post(
                "/api/earnings",
                json={
                    "folder_id": folder_id,
                    "ticker": ticker,
                    "period_type": "QUARTERLY",
                    "fiscal_quarter": "2025-Q1",
                    "period": "2025-Q1",
                    "estimate_eps": 2.35,
                    "actual_eps": 2.48,
                },
            )

        # Verify both tickers have data
        earnings_list = client.get(f"/api/folders/{folder_id}/earnings")
        assert earnings_list.json()["total"] == 2

        guidance_list = client.get(f"/api/folders/{folder_id}/guidance")
        assert guidance_list.json()["total"] == 2

        # Filter by ticker works for both
        aapl_earnings = client.get(f"/api/folders/{folder_id}/earnings?ticker=AAPL")
        assert aapl_earnings.json()["total"] == 1

        msft_guidance = client.get(f"/api/folders/{folder_id}/guidance?ticker=MSFT")
        assert msft_guidance.json()["total"] == 1
