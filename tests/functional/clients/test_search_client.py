import pytest
from diffbot_kg.clients.search import DiffbotSearchClient

from tests.functional.clients.conftest import ORG_ENTITY_ID, ORG_NAME, Secret


@pytest.fixture(scope="session")
def client(token):
    yield DiffbotSearchClient(token=token.value)


@pytest.mark.vcr(record_mode="new_episodes")
@pytest.mark.usefixtures("suppress_aiohttp_output")
class TestDiffbotSearchClient:
    # @pytest.mark.sanitize(token())
    @pytest.mark.asyncio
    async def test_search(self, token: Secret):
        # ARRANGE
        client = DiffbotSearchClient(token=token.value)

        # ACT
        response = await client.search(
            {"query": f'type:Organization strict:name:"{ORG_NAME}"'}
        )

        # ASSERT
        assert response.status == 200
        assert response.content["hits"] == 1
        assert response.content["results"] == 1
        assert response.entities[0]["id"] == ORG_ENTITY_ID

        # TEARDOWN
        await client.close()
