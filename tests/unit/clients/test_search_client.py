import pytest
from diffbot_kg.clients.search import DiffbotSearchClient
from diffbot_kg.clients.session import DiffbotSession
from diffbot_kg.models.response import DiffbotEntitiesResponse
from diffbot_kg.models.response.base import BaseDiffbotResponse

# trunk-ignore(bandit/B105)
TOKEN = "fake_token"


class TestDiffbotSearchClient:
    @pytest.fixture(scope="class")
    def client(self):
        # trunk-ignore(bandit/B106)
        return DiffbotSearchClient(token=TOKEN)

    # Returns a DiffbotResponse object when given a search query.
    @pytest.mark.asyncio
    async def test_mocked_search(self, mocker, client):
        # ARRANGE

        # Define the search query parameters
        params = {"query": "your_search_query", "limit": 10}

        # Mock the _post_or_put method
        mocker.patch.object(
            DiffbotSession,
            "get",
            return_value=BaseDiffbotResponse(200, {}, {}),  # type: ignore
        )

        # ACT
        response = await client.search(params)

        # ASSERT
        params = client.default_params | params

        DiffbotSession.get.assert_called_with(
            DiffbotSearchClient.search_url,
            params=params,
            headers={"accept": "application/json"},
        )
        assert isinstance(response, DiffbotEntitiesResponse)
        assert response.status == 200
