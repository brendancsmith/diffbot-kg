import pytest
from diffbot_kg.clients import DiffbotEnhanceClient
from diffbot_kg.clients.session import DiffbotSession
from diffbot_kg.models.response import (
    DiffbotBulkJobCreateResponse,
    DiffbotBulkJobStatusResponse,
    DiffbotEntitiesResponse,
    DiffbotListBulkJobsResponse,
)
from diffbot_kg.models.response.base import BaseDiffbotResponse
from diffbot_kg.models.response.bulkjob_results import DiffbotBulkJobResultsResponse
from diffbot_kg.models.response.coverage_report import DiffbotCoverageReportResponse

# trunk-ignore(bandit/B105)
TOKEN = "valid_token"


class TestDiffbotEnhanceClient:
    @pytest.fixture(scope="class")
    def client(self):
        # trunk-ignore(bandit/B106)
        return DiffbotEnhanceClient(token=TOKEN)

    @pytest.mark.asyncio
    async def test_enhance(self, mocker, client):
        params = {"type": "Organization", "name": "Diffbot"}

        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        response = await client.enhance(params)

        DiffbotSession.get.assert_called_with(
            DiffbotEnhanceClient.enhance_url,
            params={**params, "token": TOKEN},
            headers={},
        )
        assert isinstance(response, DiffbotEntitiesResponse)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_create_bulkjob(self, mocker, client):
        json_data = [
            {"type": "Organization", "name": "Diffbot"},
            {"type": "Organization", "name": "Acme"},
        ]

        mocker.patch.object(
            DiffbotSession,
            "post",
            return_value=BaseDiffbotResponse(202, {}, {}),  # type: ignore
        )

        response = await client.create_bulkjob(json_data)

        DiffbotSession.post.assert_called_with(
            DiffbotEnhanceClient.bulk_job_url,
            params={"token": TOKEN},
            headers={"content-type": "application/json"},
            json=json_data,
        )
        assert isinstance(response, DiffbotBulkJobCreateResponse)
        assert response.status == 202

    @pytest.mark.asyncio
    async def test_create_bulkjob_with_params(self, mocker, client):
        json_data = [{"type": "Organization", "name": "Diffbot"}]
        params = {"size": 1}

        mocker.patch.object(
            DiffbotSession,
            "post",
            return_value=BaseDiffbotResponse(202, {}, {}),  # type: ignore
        )

        response = await client.create_bulkjob(json_data, params)

        call_args = DiffbotSession.post.call_args
        assert call_args.kwargs["params"]["size"] == 1
        assert call_args.kwargs["params"]["token"] == TOKEN
        assert isinstance(response, DiffbotBulkJobCreateResponse)

    @pytest.mark.asyncio
    async def test_create_bulkjob_empty_data_raises(self, client):
        with pytest.raises(ValueError, match="data must be provided"):
            await client.create_bulkjob([])

    @pytest.mark.asyncio
    async def test_create_bulkjob_none_data_raises(self, client):
        with pytest.raises(ValueError, match="data must be provided"):
            await client.create_bulkjob(None)

    @pytest.mark.asyncio
    async def test_bulkjob_status(self, mocker, client):
        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        response = await client.bulkjob_status("job-123")

        call_url = str(DiffbotSession.get.call_args.args[0])
        assert "job-123" in call_url
        assert isinstance(response, DiffbotBulkJobStatusResponse)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_list_bulkjobs(self, mocker, client):
        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        response = await client.list_bulkjobs()

        DiffbotSession.get.assert_called_once()
        assert isinstance(response, DiffbotListBulkJobsResponse)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_bulkjob_results(self, mocker, client):
        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        response = await client.bulkjob_results("job-456")

        call_url = str(DiffbotSession.get.call_args.args[0])
        assert "job-456" in call_url
        assert isinstance(response, DiffbotBulkJobResultsResponse)

    @pytest.mark.asyncio
    async def test_single_bulkjob_result(self, mocker, client):
        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        response = await client.single_bulkjob_result("job-789", 2)

        call_url = str(DiffbotSession.get.call_args.args[0])
        assert "job-789" in call_url
        assert "2" in call_url
        assert isinstance(response, DiffbotEntitiesResponse)

    @pytest.mark.asyncio
    async def test_bulkjob_coverage_report(self, mocker, client):
        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, ""),  # type: ignore
        )

        response = await client.bulkjob_coverage_report("job-abc", "report-xyz")

        call_url = str(DiffbotSession.get.call_args.args[0])
        assert "job-abc" in call_url
        assert "report-xyz" in call_url
        assert isinstance(response, DiffbotCoverageReportResponse)

    @pytest.mark.asyncio
    async def test_stop_bulkjob(self, mocker, client):
        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        response = await client.stop_bulkjob("job-stop")

        call_url = str(DiffbotSession.get.call_args.args[0])
        assert "job-stop" in call_url
        assert "stop" in call_url
        assert isinstance(response, DiffbotBulkJobStatusResponse)
