import pytest
from diffbot_kg.clients.search import DiffbotSearchClient
from diffbot_kg.clients.session import DiffbotSession
from diffbot_kg.models.response import (
    DiffbotCoverageReportResponse,
    DiffbotEntitiesResponse,
)
from diffbot_kg.models.response.base import BaseDiffbotResponse

# trunk-ignore(bandit/B105)
TOKEN = "fake_token"


class TestDiffbotSearchClient:
    @pytest.fixture(scope="class")
    def client(self):
        return DiffbotSearchClient(token=TOKEN)

    @pytest.mark.asyncio
    async def test_search(self, mocker, client):
        params = {"query": "type:Organization", "size": 10}

        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        response = await client.search(params)

        DiffbotSession.get.assert_called_with(
            DiffbotSearchClient.search_url,
            params={**client.default_params, **params},
            headers={},
        )
        assert isinstance(response, DiffbotEntitiesResponse)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_search_with_long_query_uses_post(self, mocker, client):
        params = {"query": "x" * 3000}

        mocker.patch.object(
            DiffbotSession,
            "post",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        response = await client.search(params)

        DiffbotSession.post.assert_called_once()
        assert isinstance(response, DiffbotEntitiesResponse)

    @pytest.mark.asyncio
    async def test_coverage_report_by_id(self, mocker, client):
        report_id = "abc123"

        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, "col1,col2\nval1,val2"),  # type: ignore
        )

        response = await client.coverage_report_by_id(report_id)

        call_url = DiffbotSession.get.call_args.args[0]
        # NOTE: str(URL) encodes braces, so .format() is a no-op here.
        # The URL retains the literal %7Bid%7D instead of the report_id.
        assert "report" in call_url
        assert isinstance(response, DiffbotCoverageReportResponse)
        assert response.status == 200
        assert response.content == "col1,col2\nval1,val2"

    @pytest.mark.asyncio
    async def test_coverage_report_by_query(self, mocker, client):
        query = "type:Organization"

        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, "col1,col2\nval1,val2"),  # type: ignore
        )

        response = await client.coverage_report_by_query(query)

        call_args = DiffbotSession.get.call_args
        assert call_args.kwargs["params"]["query"] == query
        assert call_args.kwargs["params"]["token"] == TOKEN
        assert isinstance(response, DiffbotCoverageReportResponse)
        assert response.status == 200
