from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientResponseError, RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from diffbot_kg.clients.session import (
    DiffbotSession,
    RetryableException,
    URLTooLongException,
)
from diffbot_kg.models.response.base import BaseDiffbotResponse


def _make_error_info(status):
    return ClientResponseError(
        request_info=RequestInfo(
            url=URL("https://example.com"),
            method="GET",
            headers=CIMultiDictProxy(CIMultiDict()),
            real_url=URL("https://example.com"),
        ),
        history=(),
        status=status,
    )


def _make_response(status=200, content_type="application/json", json_data=None, headers=None):
    """Create a mock aiohttp response."""
    resp = MagicMock()
    resp.status = status
    resp.reason = "OK" if status == 200 else "Error"
    resp.content_type = content_type
    resp.json = AsyncMock(return_value=json_data or {})
    resp.text = AsyncMock(return_value="")

    raw_headers = CIMultiDict(headers or {})
    resp.headers = CIMultiDictProxy(raw_headers)

    if status >= 400:
        resp.raise_for_status = MagicMock(side_effect=_make_error_info(status))
    else:
        resp.raise_for_status = MagicMock()

    # Support async context manager (await session.request() returns this)
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)

    return resp


class TestDiffbotSession:
    @pytest.fixture
    def session(self):
        return DiffbotSession()

    def test_initial_state(self, session):
        assert session.is_open is False

    @pytest.mark.asyncio
    async def test_open(self, session):
        await session.open()

        assert session.is_open is True
        assert session._session is not None
        assert session._limiter is not None

        await session.close()

    @pytest.mark.asyncio
    async def test_close(self, session):
        await session.open()
        await session.close()

        assert session.is_open is False

    @pytest.mark.asyncio
    async def test_get_auto_opens(self, mocker, session):
        mock_resp = _make_response(200, json_data={"data": []})
        mock_request = AsyncMock(return_value=mock_resp)

        await session.open()
        mocker.patch.object(session._session, "request", mock_request)

        response = await session.get("https://example.com")

        assert session.is_open is True
        assert isinstance(response, BaseDiffbotResponse)
        mock_request.assert_called_once()

        await session.close()

    @pytest.mark.asyncio
    async def test_post_auto_opens(self, mocker, session):
        mock_resp = _make_response(200, json_data={"result": "ok"})
        mock_request = AsyncMock(return_value=mock_resp)

        await session.open()
        mocker.patch.object(session._session, "request", mock_request)

        response = await session.post("https://example.com", json={"q": "test"})

        assert session.is_open is True
        assert isinstance(response, BaseDiffbotResponse)

        await session.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        session = DiffbotSession()
        await session.open()
        async with session:
            assert session.is_open is True
        assert session.is_open is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", [408, 429, 500, 502, 503])
    async def test_retryable_status_codes(self, mocker, status):
        session = DiffbotSession()
        mock_resp = _make_response(status)
        mock_request = AsyncMock(return_value=mock_resp)

        await session.open()
        mocker.patch.object(session._session, "request", mock_request)

        with pytest.raises(RetryableException):
            await session._request("GET", "https://example.com")

        await session.close()

    @pytest.mark.asyncio
    async def test_url_too_long_exception(self, mocker, session):
        mock_resp = _make_response(414)
        mock_request = AsyncMock(return_value=mock_resp)

        await session.open()
        mocker.patch.object(session._session, "request", mock_request)

        with pytest.raises(URLTooLongException):
            await session._request("GET", "https://example.com")

        await session.close()

    @pytest.mark.asyncio
    async def test_non_retryable_error_reraises(self, mocker, session):
        mock_resp = _make_response(403)
        mock_request = AsyncMock(return_value=mock_resp)

        await session.open()
        mocker.patch.object(session._session, "request", mock_request)

        with pytest.raises(ClientResponseError):
            await session._request("GET", "https://example.com")

        await session.close()

    @pytest.mark.asyncio
    async def test_successful_response(self, mocker, session):
        mock_resp = _make_response(200, json_data={"hits": 1})
        mock_request = AsyncMock(return_value=mock_resp)

        await session.open()
        mocker.patch.object(session._session, "request", mock_request)

        response = await session._request("GET", "https://example.com")

        assert isinstance(response, BaseDiffbotResponse)
        assert response.status == 200

        await session.close()
