import json
import logging
from typing import Any, Self, cast

import aiohttp
from multidict import CIMultiDictProxy

log = logging.getLogger(__name__)


class BaseDiffbotResponse:
    def __init__(
        self,
        status: int,
        headers: CIMultiDictProxy[str],
        content: dict[str, Any] | list[dict[str, Any]] | str,
    ):
        self.status = status
        self.headers = headers
        self.content = content

    @classmethod
    async def create(cls, resp: aiohttp.ClientResponse) -> Self:
        """Unpack an aiohttp response object and return a BaseDiffbotResponse instance."""

        if resp.content_type == "application/json":
            content = await resp.json()
        elif resp.content_type == "application/json-lines":
            text = await resp.text()
            content = [json.loads(line) for line in text.strip().split("\n")]
        else:
            content = await resp.text()
        return cls(resp.status, resp.headers, content)


class BaseJsonDiffbotResponse(BaseDiffbotResponse):
    def __init__(
        self, status: int, headers: CIMultiDictProxy[str], content: dict[str, Any]
    ):
        super().__init__(status, headers, content)

        self.content = cast(dict[str, Any], content)


class BaseJsonLinesDiffbotResponse(BaseDiffbotResponse):
    def __init__(
        self, status: int, headers: CIMultiDictProxy[str], content: list[dict[str, Any]]
    ):
        super().__init__(status, headers, content)

        self.content = cast(list[dict[str, Any]], content)


class BaseTextDiffbotResponse(BaseDiffbotResponse):
    def __init__(self, status: int, headers: CIMultiDictProxy[str], content: str):
        super().__init__(status, headers, content)

        self.content = cast(str, content)
