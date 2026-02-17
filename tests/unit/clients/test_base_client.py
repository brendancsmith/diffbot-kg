import pytest
from diffbot_kg.clients.base import BaseDiffbotKGClient
from diffbot_kg.clients.session import DiffbotSession
from diffbot_kg.models.response.base import BaseDiffbotResponse

# trunk-ignore(bandit/B105)
TOKEN = "test_token"


class TestBaseDiffbotKGClient:
    @pytest.fixture
    def client(self):
        return BaseDiffbotKGClient(token=TOKEN)

    @pytest.fixture
    def client_with_defaults(self):
        return BaseDiffbotKGClient(token=TOKEN, size=25, nonCanonicalized="true")

    def test_init_stores_token(self, client):
        assert client.default_params["token"] == TOKEN

    def test_init_stores_default_params(self, client_with_defaults):
        assert client_with_defaults.default_params["token"] == TOKEN
        assert client_with_defaults.default_params["size"] == 25
        assert client_with_defaults.default_params["nonCanonicalized"] == "true"

    def test_init_creates_session(self, client):
        assert isinstance(client.s, DiffbotSession)

    def test_merge_params_adds_defaults(self, client):
        result = client._merge_params({"query": "test"})
        assert result == {"token": TOKEN, "query": "test"}

    def test_merge_params_request_overrides_defaults(self, client_with_defaults):
        result = client_with_defaults._merge_params({"size": 50})
        assert result["size"] == 50
        assert result["token"] == TOKEN

    def test_merge_params_filters_none_values(self, client):
        result = client._merge_params({"query": "test", "filter": None})
        assert "filter" not in result

    def test_merge_params_with_none_input(self, client):
        result = client._merge_params(None)
        assert result == {"token": TOKEN}

    @pytest.mark.asyncio
    async def test_get_merges_params(self, mocker, client):
        mock_resp = BaseDiffbotResponse(200, {}, {})  # type: ignore
        mocker.patch.object(DiffbotSession, "get", return_value=mock_resp)

        url = BaseDiffbotKGClient.url / "test"
        await client._get(url, params={"q": "hello"})

        DiffbotSession.get.assert_called_with(
            url, params={"token": TOKEN, "q": "hello"}, headers={}
        )

    @pytest.mark.asyncio
    async def test_get_default_headers(self, mocker, client):
        mock_resp = BaseDiffbotResponse(200, {}, {})  # type: ignore
        mocker.patch.object(DiffbotSession, "get", return_value=mock_resp)

        await client._get(BaseDiffbotKGClient.url, headers=None)

        call_args = DiffbotSession.get.call_args
        assert call_args.kwargs["headers"] == {}

    @pytest.mark.asyncio
    async def test_post_sets_content_type(self, mocker, client):
        mock_resp = BaseDiffbotResponse(200, {}, {})  # type: ignore
        mocker.patch.object(DiffbotSession, "post", return_value=mock_resp)

        await client._post(BaseDiffbotKGClient.url, json={"key": "val"})

        call_args = DiffbotSession.post.call_args
        assert call_args.kwargs["headers"]["content-type"] == "application/json"

    @pytest.mark.asyncio
    async def test_post_preserves_custom_headers(self, mocker, client):
        mock_resp = BaseDiffbotResponse(200, {}, {})  # type: ignore
        mocker.patch.object(DiffbotSession, "post", return_value=mock_resp)

        await client._post(
            BaseDiffbotKGClient.url,
            json={},
            headers={"x-custom": "val"},
        )

        call_args = DiffbotSession.post.call_args
        assert call_args.kwargs["headers"]["content-type"] == "application/json"
        assert call_args.kwargs["headers"]["x-custom"] == "val"

    @pytest.mark.asyncio
    async def test_get_or_post_short_url_uses_get(self, mocker, client):
        mock_resp = BaseDiffbotResponse(200, {}, {})  # type: ignore
        mocker.patch.object(DiffbotSession, "get", return_value=mock_resp)

        await client._get_or_post(BaseDiffbotKGClient.url, params={"q": "short"})

        DiffbotSession.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_or_post_long_url_uses_post(self, mocker, client):
        mock_resp = BaseDiffbotResponse(200, {}, {})  # type: ignore
        mocker.patch.object(DiffbotSession, "post", return_value=mock_resp)

        long_query = "x" * 3000
        await client._get_or_post(BaseDiffbotKGClient.url, params={"q": long_query})

        DiffbotSession.post.assert_called_once()
        call_args = DiffbotSession.post.call_args
        # Token should be in params, query should be in json body
        assert call_args.kwargs["params"] == {"token": TOKEN}
        assert call_args.kwargs["json"]["q"] == long_query

    @pytest.mark.asyncio
    async def test_close_delegates_to_session(self, mocker, client):
        mocker.patch.object(DiffbotSession, "close")

        await client.close()

        DiffbotSession.close.assert_called_once()
