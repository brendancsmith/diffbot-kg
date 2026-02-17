import pytest
from diffbot_kg.clients import DiffbotEnhanceClient
from diffbot_kg.clients.session import DiffbotSession
from diffbot_kg.models.response import DiffbotEntitiesResponse
from diffbot_kg.models.response.base import BaseDiffbotResponse
from diffbot_kg.models.response.bulkjob_create import DiffbotBulkJobCreateResponse


class TestDiffbotEnhanceClient:
    @pytest.fixture(scope="class")
    def client(self):
        # trunk-ignore(bandit/B106)
        return DiffbotEnhanceClient(token="valid_token")

    @pytest.mark.asyncio
    async def test_mocked_enhance(self, mocker, client):
        # ARRANGE

        # Define the search query parameters
        params = {"query": "your_search_query", "size": 10}

        # Mock the _post_or_put method
        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        # ACT
        response = await client.enhance(params)

        # ASSERT
        DiffbotSession.get.assert_called_with(
            DiffbotEnhanceClient.enhance_url,
            params={**params, "token": "valid_token"},
            headers={}
        )
        assert isinstance(response, DiffbotEntitiesResponse)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_mocked_create_bulkjob(self, mocker, client):
        # ARRANGE

        # Define the search query parameters
        params = {"query": "your_bulk_enhance_query", "size": 10}

        # Mock the _post_or_put method
        mocker.patch.object(
            DiffbotSession,
            "post",
            return_value=BaseDiffbotResponse(202, {}, {}),  # type: ignore
        )

        # ACT
        response = await client.create_bulkjob(params)

        # ASSERT
        DiffbotSession.post.assert_called_with(
            DiffbotEnhanceClient.bulk_job_url,
            params={"token": "valid_token"},
            headers={"content-type": "application/json"},
            json=params
        )
        assert isinstance(response, DiffbotBulkJobCreateResponse)
        assert response.status == 202
