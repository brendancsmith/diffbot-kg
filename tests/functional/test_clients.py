import os

import dotenv
import pytest
from diffbot_kg.clients import DiffbotEnhanceClient, DiffbotSearchClient

ORG_NAME = "Diffbot"
ORG_ENTITY_ID = "EYX1i02YVPsuT7fPLUYgRhQ"


class Secret:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Secret(********)"

    def __str___(self):
        return "*******"


@pytest.fixture(scope="session", autouse=True)
def token():
    __tracebackhide__ = True
    dotenv.load_dotenv(override=True)
    return Secret(os.environ.get("DIFFBOT_TOKEN"))


@pytest.hookimpl(tryfirst=True)
def pytest_sanitize_hook(items):
    secrets = [token()]
    for item in items:
        for secret in secrets:
            item.add_marker(pytest.mark.sanitize(secret))


# @pytest.mark.usefixtures("suppress_aiottp_output")
class TestDiffbotSearchClient:
    @pytest.mark.asyncio
    @pytest.mark.vcr
    # @pytest.mark.sanitize(token())
    async def test_search_client_search(self, token):
        client = DiffbotSearchClient(token=token.value)
        response = await client.search(
            {"query": f'type:Organization strict:name:"{ORG_NAME}"'}
        )
        assert response.status == 200
        assert response.content["hits"] == 1
        assert response.content["results"] == 1
        assert response.data[0]["entity"]["id"] == ORG_ENTITY_ID


# @pytest.mark.usefixtures("suppress_aiottp_output")
class TestDiffbotEnhanceClient:
    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_enhance_client_enhance(self, token):
        client = DiffbotEnhanceClient(token=token.value)
        response = await client.enhance({"type": "Organization", "name": ORG_NAME})
        assert response.status == 200
        assert response.content["hits"] == 1
        assert response.data[0]["entity"]["id"] == ORG_ENTITY_ID

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_enhance_client_create_bulkjob(self, token):
        import logging

        logging.basicConfig(level=logging.CRITICAL)
        logging.getLogger("diffbot_kg").setLevel(logging.CRITICAL)

        logging.getLogger("diffbot_kg.session").setLevel(logging.CRITICAL)
        logging.getLogger("diffbot_kg.clients").setLevel(logging.CRITICAL)
        client = DiffbotEnhanceClient(token=token.value)
        response = await client.create_bulkjob({"uris": ["http://diffbot.com"]})
        assert response.status == 200
        assert "bulkJobId" in response.content
