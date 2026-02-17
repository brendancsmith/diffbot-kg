from unittest.mock import AsyncMock, PropertyMock

import pytest
from multidict import CIMultiDict, CIMultiDictProxy

from diffbot_kg.models.response.base import (
    BaseDiffbotResponse,
    BaseJsonDiffbotResponse,
    BaseJsonLinesDiffbotResponse,
    BaseTextDiffbotResponse,
)
from diffbot_kg.models.response.bulkjob_create import DiffbotBulkJobCreateResponse
from diffbot_kg.models.response.bulkjob_results import DiffbotBulkJobResultsResponse
from diffbot_kg.models.response.bulkjob_status import DiffbotBulkJobStatusResponse
from diffbot_kg.models.response.entities import DiffbotEntitiesResponse


def _mock_headers(extra=None):
    return CIMultiDictProxy(CIMultiDict(extra or {}))


def _mock_aiohttp_response(content_type, json_data=None, text_data="", status=200, headers=None):
    resp = AsyncMock()
    resp.status = status
    resp.content_type = content_type
    resp.headers = _mock_headers(headers)
    resp.json = AsyncMock(return_value=json_data)
    resp.text = AsyncMock(return_value=text_data)
    return resp


class TestBaseDiffbotResponse:
    def test_init(self):
        resp = BaseDiffbotResponse(200, _mock_headers(), {"key": "val"})
        assert resp.status == 200
        assert resp.content == {"key": "val"}

    @pytest.mark.asyncio
    async def test_create_json(self):
        mock = _mock_aiohttp_response(
            "application/json", json_data={"hits": 5, "data": []}
        )

        resp = await BaseDiffbotResponse.create(mock)

        assert resp.status == 200
        assert resp.content == {"hits": 5, "data": []}
        mock.json.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_json_lines(self):
        lines = '{"id": 1}\n{"id": 2}\n{"id": 3}'
        mock = _mock_aiohttp_response("application/json-lines", text_data=lines)

        resp = await BaseDiffbotResponse.create(mock)

        assert resp.status == 200
        assert isinstance(resp.content, list)
        assert len(resp.content) == 3
        assert resp.content[0] == {"id": 1}
        assert resp.content[2] == {"id": 3}

    @pytest.mark.asyncio
    async def test_create_text(self):
        mock = _mock_aiohttp_response("text/csv", text_data="col1,col2\nval1,val2")

        resp = await BaseDiffbotResponse.create(mock)

        assert resp.status == 200
        assert resp.content == "col1,col2\nval1,val2"
        mock.text.assert_awaited_once()


class TestBaseJsonDiffbotResponse:
    def test_content_type(self):
        resp = BaseJsonDiffbotResponse(200, _mock_headers(), {"key": "val"})
        assert resp.content == {"key": "val"}


class TestBaseJsonLinesDiffbotResponse:
    def test_content_type(self):
        resp = BaseJsonLinesDiffbotResponse(200, _mock_headers(), [{"a": 1}, {"b": 2}])
        assert resp.content == [{"a": 1}, {"b": 2}]


class TestBaseTextDiffbotResponse:
    def test_content_type(self):
        resp = BaseTextDiffbotResponse(200, _mock_headers(), "plain text")
        assert resp.content == "plain text"


class TestDiffbotEntitiesResponse:
    def test_data(self):
        content = {"data": [{"entity": {"id": "1"}}, {"entity": {"id": "2"}}]}
        resp = DiffbotEntitiesResponse(200, _mock_headers(), content)

        assert len(resp.data) == 2
        assert resp.data[0]["entity"]["id"] == "1"

    def test_entities(self):
        content = {
            "data": [
                {"entity": {"id": "e1", "name": "Org1"}},
                {"entity": {"id": "e2", "name": "Org2"}},
            ]
        }
        resp = DiffbotEntitiesResponse(200, _mock_headers(), content)

        assert len(resp.entities) == 2
        assert resp.entities[0]["id"] == "e1"
        assert resp.entities[1]["name"] == "Org2"


class TestDiffbotBulkJobCreateResponse:
    def test_job_id(self):
        content = {"job_id": "bulk-123", "status": "CREATED"}
        resp = DiffbotBulkJobCreateResponse(200, _mock_headers(), content)

        assert resp.jobId == "bulk-123"


class TestDiffbotBulkJobStatusResponse:
    def test_job_id(self):
        content = {"content": {"job_id": "job-456", "status": "RUNNING", "reports": []}}
        resp = DiffbotBulkJobStatusResponse(200, _mock_headers(), content)

        assert resp.jobId == "job-456"

    def test_complete_true(self):
        content = {"content": {"job_id": "job-456", "status": "COMPLETE", "reports": []}}
        resp = DiffbotBulkJobStatusResponse(200, _mock_headers(), content)

        assert resp.complete is True

    def test_complete_false(self):
        content = {"content": {"job_id": "job-456", "status": "RUNNING", "reports": []}}
        resp = DiffbotBulkJobStatusResponse(200, _mock_headers(), content)

        assert resp.complete is False

    def test_reports(self):
        reports = [{"reportId": "r1"}, {"reportId": "r2"}]
        content = {"content": {"job_id": "j", "status": "COMPLETE", "reports": reports}}
        resp = DiffbotBulkJobStatusResponse(200, _mock_headers(), content)

        assert len(resp.reports) == 2
        assert resp.reports[0]["reportId"] == "r1"


class TestDiffbotBulkJobResultsResponse:
    @pytest.fixture
    def results_content(self):
        return [
            {
                "request_ctx": {"query_ctx": {"bulkjobId": "bulk-789"}},
                "hits": 1,
                "data": [{"entity": {"id": "e1"}}],
            },
            {
                "request_ctx": {},
                "hits": 1,
                "data": [{"entity": {"id": "e2"}}],
            },
        ]

    def test_job_id(self, results_content):
        headers = _mock_headers({"X-Diffbot-ReportId": "rpt-1"})
        resp = DiffbotBulkJobResultsResponse(200, headers, results_content)

        assert resp.jobId == "bulk-789"

    def test_job_id_missing_raises(self):
        content = [{"request_ctx": {}, "data": []}]
        headers = _mock_headers()
        resp = DiffbotBulkJobResultsResponse(200, headers, content)

        with pytest.raises(RuntimeError, match="No bulkJobId found"):
            _ = resp.jobId

    def test_report_id(self, results_content):
        headers = _mock_headers({"X-Diffbot-ReportId": "rpt-abc"})
        resp = DiffbotBulkJobResultsResponse(200, headers, results_content)

        assert resp.reportId == "rpt-abc"

    def test_entities(self, results_content):
        headers = _mock_headers({"X-Diffbot-ReportId": "rpt-1"})
        resp = DiffbotBulkJobResultsResponse(200, headers, results_content)

        assert len(resp.entities) == 2
        assert resp.entities[0]["id"] == "e1"
        assert resp.entities[1]["id"] == "e2"
