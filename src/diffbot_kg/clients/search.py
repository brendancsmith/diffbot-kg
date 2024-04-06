from typing import cast

from diffbot_kg.clients.base import BaseDiffbotKGClient
from diffbot_kg.models.response import (
    DiffbotCoverageReportResponse,
    DiffbotEntitiesResponse,
)


class DiffbotSearchClient(BaseDiffbotKGClient):
    """
    A client for interacting with Diffbot's Knowledge Graph search API.
    """

    search_url = BaseDiffbotKGClient.url / "dql"
    report_url = search_url / "report"
    report_by_id_url = report_url / "{id}"

    async def search(self, params: dict) -> DiffbotEntitiesResponse:
        """Search Diffbot's Knowledge Graph.

        Args:
            params (dict): Dict of params to send in request

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        # No change needed here; the issue will be addressed in the session handling
        resp = await self._get_or_post(self.search_url, params=params)
        resp.__class__ = DiffbotEntitiesResponse
        return cast(DiffbotEntitiesResponse, resp)

    async def coverage_report_by_id(
        self, report_id: str
    ) -> DiffbotCoverageReportResponse:
        """Download coverage report by report ID.

        Args:
            report_id (str): The report ID string.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        url = str(self.report_by_id_url).format(id=report_id)
        resp = await self._get(url)
        resp.__class__ = DiffbotCoverageReportResponse
        return cast(DiffbotCoverageReportResponse, resp)

    async def coverage_report_by_query(
        self, query: str
    ) -> DiffbotCoverageReportResponse:
        """Download coverage report by DQL query.

        Args:
            query (str): The DQL query string.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        params = {"query": query}
        resp = await self._get(self.report_url, params=params)
        resp.__class__ = DiffbotCoverageReportResponse
        return cast(DiffbotCoverageReportResponse, resp)
