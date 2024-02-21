import logging
from http import HTTPMethod
from typing import Any, List, Self

import aiohttp
import aiolimiter
from multidict import CIMultiDictProxy
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

log = logging.getLogger(__name__)


class DiffbotResponse:
    """DiffbotResponse represents the response from a Diffbot API request.

    It contains the response status, headers, and JSON content. Provides
    convenience properties to access the 'data' and 'entities' portions
    of the JSON content.

    The create classmethod is the main constructor, which handles converting
    an aiohttp response into a DiffbotResponse.
    """

    def __init__(
        self, status: int, headers: CIMultiDictProxy[str], content: dict[str, Any]
    ):
        self.status = status
        self.headers = headers
        self.content = content

    @property
    def data(self) -> List[dict]:
        return self.content["data"]

    @property
    def entities(self) -> List[dict]:
        # Note: this class/method will not be compatible with facet queries
        # (no entities returned)
        return [d["entity"] for d in self.data]

    @classmethod
    async def create(cls, resp: aiohttp.ClientResponse) -> Self:
        """Unpack an aiohttp response object and return a DiffbotResponse instance."""
        return cls(resp.status, resp.headers, await resp.json())


class RetryableException(Exception):
    pass


# TODO: should I make this a subclass of ClientSession?
class DiffbotSession:
    """
    A class representing a session with the Diffbot API.

    Attributes:
        _session (aiohttp.ClientSession): The underlying HTTP client session.
        _limiter (aiolimiter.AsyncLimiter): The rate limiter used to limit the number of requests per second.
    """

    def __init__(self) -> None:
        headers = {"accept": "application/json"}
        timeout = aiohttp.ClientTimeout(total=60, sock_connect=5)
        self._session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        self._limiter = aiolimiter.AsyncLimiter(max_rate=5, time_period=1)

    async def get(self, url, **kwargs) -> DiffbotResponse:
        resp = await self._request(HTTPMethod.GET, url, **kwargs)
        return resp

    async def post(self, url, **kwargs) -> DiffbotResponse:
        resp = await self._request(HTTPMethod.POST, url, **kwargs)
        return resp

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()

    @retry(
        retry=retry_if_exception_type(RetryableException),
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(multiplier=0.5, min=2, max=30),
        after=after_log(log, logging.DEBUG),
    )
    async def _request(self, method, url, **kwargs) -> DiffbotResponse:
        # TODO: Implement retries on [400, 422, 429, 500] status codes using Tenancity lib
        async with self._limiter:
            async with await self._session.request(method, url, **kwargs) as resp:
                try:
                    resp.raise_for_status()
                except Exception as e:
                    if resp.status in [408, 429] or resp.status >= 500:
                        log.debug(
                            "Retryable exception: %s (%s %s %s)",
                            e,
                            resp.status,
                            resp.reason,
                            resp.headers,
                        )
                        raise RetryableException from e

                    log.exception(
                        "%s (%s %s %s)", e, resp.status, resp.reason, resp.headers
                    )
                    raise e

                return await DiffbotResponse.create(resp)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.close()
