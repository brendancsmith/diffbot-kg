import logging
from http import HTTPMethod
from typing import Self

import aiohttp
import aiolimiter
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from diffbot_kg.models.response.base import BaseDiffbotResponse

log = logging.getLogger(__name__)


class RetryableException(Exception):
    pass


class URLTooLongException(Exception):
    pass


# TODO: Should this be a subclass of ClientSession?
class DiffbotSession:
    """
    A class representing a session with the Diffbot API.

    Attributes:
        _session (aiohttp.ClientSession): The underlying HTTP client session.
        _limiter (aiolimiter.AsyncLimiter): The rate limiter used to limit the number of requests per second.
    """

    def __init__(self) -> None:
        self._headers = {"accept": "application/json"}
        self._timeout = aiohttp.ClientTimeout(total=60, sock_connect=5)

        self.is_open = False

    async def open(self) -> Self:
        self._session = aiohttp.ClientSession(headers=self._headers, timeout=self._timeout)
        self._limiter = aiolimiter.AsyncLimiter(max_rate=5, time_period=1)

        self.is_open = True
        return self

    async def get(self, url, **kwargs) -> BaseDiffbotResponse:
        if not self.is_open:
            await self.open()

        # sourcery skip: inline-immediately-returned-variable
        resp = await self._request(HTTPMethod.GET, url, **kwargs)
        return resp

    async def post(self, url, **kwargs) -> BaseDiffbotResponse:
        if not self.is_open:
            await self.open()

        # sourcery skip: inline-immediately-returned-variable
        resp = await self._request(HTTPMethod.POST, url, **kwargs)
        return resp

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()

        self.is_open = False

    @retry(
        retry=retry_if_exception_type(RetryableException),
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_random_exponential(multiplier=0.5, min=2, max=30),
        after=after_log(log, logging.DEBUG),
    )
    async def _request(self, method, url, **kwargs) -> BaseDiffbotResponse:
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

                    elif resp.status == 414:
                        log.debug(
                            "URLTooLongException: %s (%s %s %s)",
                            e,
                            resp.status,
                            resp.reason,
                            resp.headers,
                        )

                        raise URLTooLongException from e

                    log.exception(
                        "%s (%s %s %s)", e, resp.status, resp.reason, resp.headers
                    )
                    raise e

                return await BaseDiffbotResponse.create(resp)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.close()
