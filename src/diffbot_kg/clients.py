import logging
from typing import Any

from yarl import URL

from diffbot_kg.session import DiffbotResponse, DiffbotSession

log = logging.getLogger(__name__)


class BaseDiffbotKGClient:
    url = URL("https://kg.diffbot.com/kg/v3/")

    def __init__(self, token, **kwargs) -> None:
        for kwarg in kwargs:
            if kwarg not in ["token", "useCache", "jsonmode", "size"]:
                raise ValueError(f"Invalid kwarg: {kwarg}")

        self.default_params = {"token": token, **kwargs}
        self.s = DiffbotSession()

    def _merge_params(self, params) -> dict[str, Any]:
        params = params or {}
        params = {**self.default_params, **params}
        params = {k: v for k, v in params.items() if v is not None}
        return params

    async def _get(self, url: str | URL, params=None, headers=None) -> DiffbotResponse:
        resp = await self.s.get(str(url), params=params, headers=headers)
        return resp

    async def _post(
        self, url: str | URL, params: dict | None = None
    ) -> DiffbotResponse:
        """POST request to Diffbot API as alternative to GET for large queries.
        All params except token are placed in the body of the request."""

        token = params.pop("token", None) if params else None
        json, params = params, {"token": token}

        # headers = {"accept": "application/json", "content-type": "application/json"}
        headers = {"content-type": "application/json"}

        resp = await self.s.post(str(url), params=params, headers=headers, json=json)
        return resp

    async def _post_or_put(self, url: str | URL, params: dict | None = None):
        # Diffbot uses nginx, which has a 4096 byte limit on URL by default
        # but there are other factors, so we'll play it safe.
        # 250 chars == 2000 bytes
        if params is None:
            params = {}
        else:
            params = {k: v for k, v in params.items() if v is not None}

        url_len = len(str(url % params))
        if url_len > 250:
            resp = await self._post(url, params=params)
        else:
            resp = await self._get(url, params=params)

        return resp


class DiffbotSearchClient(BaseDiffbotKGClient):
    search_url = BaseDiffbotKGClient.url / "dql"
    report_url = BaseDiffbotKGClient.url / "dql/report"
    report_by_id_url = BaseDiffbotKGClient.url / "dql/report/{id}"

    async def search(self, params: dict) -> DiffbotResponse:
        """Search Dreport_urliffbot's Knowledge Graph.

        Args:
            params (dict): Dict of params to send in request

        Returns:
            response: requests.Response object
        """
        resp = await self._post_or_put(self.search_url, params=params)

        return resp

    async def coverage_report_by_id(self, report_id: str) -> DiffbotResponse:
        """Download coverage report by report ID.

        Args:
            report_id (str): The report ID string.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """
        url = str(self.report_by_id_url).format(id=report_id)
        resp = await self._get(url)
        return resp

    async def coverage_report_by_query(self, query: str) -> DiffbotResponse:
        """Download coverage report by DQL query.

        Args:
            query (str): The DQL query string.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """
        params = {"query": query}
        resp = await self._get(self.report_url, params=params)
        return resp


class DiffbotEnhanceClient(BaseDiffbotKGClient):
    enhance_url = BaseDiffbotKGClient.url / "enhance"
    bulk_enhance_url = enhance_url / "bulk"
    bulk_status_url = BaseDiffbotKGClient.url / "enhance/bulk/status"
    single_bulkjob_result_url = (
        BaseDiffbotKGClient.url / "enhance/bulk/{bulkjobId}/{jobIdx}"
    )
    bulk_job_results_url = BaseDiffbotKGClient.url / "enhance/bulk/{bulkjobId}"
    bulk_job_coverage_report_url = (
        BaseDiffbotKGClient.url / "enhance/bulk/{bulkjobId}/coverage/{reportId}"
    )

    async def enhance(self, params) -> DiffbotResponse:
        resp = await self._get(self.enhance_url, params=params)
        return resp

    bulk_job_stop_url = BaseDiffbotKGClient.url / "enhance/bulk/{bulkjobId}/stop"
    ...  # Other methods

    async def stop_bulkjob(self, bulkjobId: str) -> DiffbotResponse:
        """
        Stop an active Enhance Bulkjob by its ID.

        Args:
            bulkjobId (str): The ID of the bulk job.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """
        url = str(self.bulk_job_stop_url).format(bulkjobId=bulkjobId)
        return await self._get(url)

    async def download_single_bulkjob_result(
        self, bulkjobId: str, jobIdx: str
    ) -> DiffbotResponse:
        """
        Download the result of a single job within a bulkjob by specifying the index of the job.

        Args:
            bulkjobId (str): The ID of the bulk job.
            jobIdx (str): The index of the job within the bulk job.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """
        url = str(self.single_bulkjob_result_url).format(
            bulkjobId=bulkjobId, jobIdx=jobIdx
        )
        return await self._get(url)

    async def create_bulkjob(self, params) -> DiffbotResponse:
        resp = await self._post(self.bulk_enhance_url, params=params)
        return resp

    async def list_bulkjobs_for_token(self) -> DiffbotResponse:
        """
        Poll the status of all Enhance Bulkjobs for a token.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """
        return await self._get(self.bulk_status_url)

    async def poll_bulkjob_status(self, bulkjobId: str) -> DiffbotResponse:
        """
        Poll the status of an Enhance Bulkjob by its ID.

        Args:
            bulkjobId (str): The ID of the bulk job.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """
        url = str(self.bulk_status_url).format(bulkjobId=bulkjobId)
        return await self._get(url)

    async def download_bulkjob_results(self, bulkjobId: str) -> DiffbotResponse:
        """
        Download the results of a completed Enhance Bulkjob by its ID.

        Args:
            bulkjobId (str): The ID of the bulk job.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """
        url = str(self.bulk_job_results_url).format(bulkjobId=bulkjobId)
        return await self._get(url)

    async def download_bulkjob_coverage_report(
        self, bulkjobId: str, reportId: str
    ) -> DiffbotResponse:
        """
        Download the coverage report of a completed Enhance Bulkjob by its ID and report ID.

        Args:
            bulkjobId (str): The ID of the bulk job.
            reportId (str): The ID of the report.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """
        url = str(self.bulk_job_coverage_report_url).format(
            bulkjobId=bulkjobId, reportId=reportId
        )
        return await self._get(url)
