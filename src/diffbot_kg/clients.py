import logging
from typing import Any

from yarl import URL

from diffbot_kg.session import DiffbotResponse, DiffbotSession

log = logging.getLogger(__name__)


class BaseDiffbotKGClient:
    """
    Base class for Diffbot Knowledge Graph API clients.
    """

    url = URL("https://kg.diffbot.com/kg/v3/", encoded=True)
    param_keys = ["jsonmode", "nonCanonicalFacts", "size"]

    def __init__(self, token, **default_params) -> None:
        """
        Initializes a new instance of the BaseDiffbotKGClient class (only
        callable by subclasses).

        Args:
            token (str): The API token for authentication.
            **default_params: Default parameters for API requests.

        Raises:
            ValueError: If an invalid keyword argument is provided.
        """

        for param in default_params:
            if param not in self.param_keys:
                raise ValueError(f"Invalid param: {param}")

        self.default_params = {"token": token, **default_params}
        self.s = DiffbotSession()

    def _merge_params(self, params) -> dict[str, Any]:
        """
        Merges the given parameters with the default parameters.

        Args:
            params (dict): The parameters to merge.

        Returns:
            dict: The merged parameters.
        """

        params = params or {}
        params = {**self.default_params, **params}
        params = {k: v for k, v in params.items() if v is not None}
        return params

    async def _get(self, url: str | URL, params=None, headers=None) -> DiffbotResponse:
        """
        Sends a GET request to the Diffbot API.

        Args:
            url (str | URL): The URL to send the request to.
            params (dict, optional): The query parameters for the request. Defaults to None.
            headers (dict, optional): The headers for the request. Defaults to None.

        Returns:
            DiffbotResponse: The response from the API.
        """

        params = self._merge_params(params)
        resp = await self.s.get(str(url), params=params, headers=headers)
        return resp

    async def _post(
        self, url: str | URL, params: dict | None = None, data: dict | None = None
    ) -> DiffbotResponse:
        """
        Sends a POST request to the Diffbot API.

        Args:
            url (str | URL): The URL to send the request to.
            params (dict, optional): The query parameters for the request. Defaults to None.
            data (dict, optional): The data for the request body. Defaults to None.

        Returns:
            DiffbotResponse: The response from the API.
        """

        params = self._merge_params(params)

        token = params.pop("token", None) if params else None
        json, params = params, {"token": token}

        headers = {"content-type": "application/json"}

        resp = await self.s.post(str(url), params=params, headers=headers, json=json)
        return resp

    async def _get_or_post(self, url: str | URL, params: dict | None = None):
        """
        Sends a GET or POST request to the Diffbot API, depending on the length of the URL.

        Args:
            url (str | URL): The URL to send the request to.
            params (dict, optional): The query parameters for the request. Defaults to None.

        Returns:
            DiffbotResponse: The response from the API.
        """

        params = self._merge_params(params)

        url_len = len(bytes(str(url % params), encoding="ascii"))

        if url_len <= 3000:
            return await self._get(url, params=params)
        else:
            return await self._post(url, params=params)


class DiffbotSearchClient(BaseDiffbotKGClient):
    """
    A client for interacting with Diffbot's Knowledge Graph search API.
    """

    search_url = BaseDiffbotKGClient.url / "dql"
    report_url = search_url / "report"
    report_by_id_url = report_url / "{id}"

    async def search(self, params: dict) -> DiffbotResponse:
        """Search Diffbot's Knowledge Graph.

        Args:
            params (dict): Dict of params to send in request

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        # params["query"] = quote(params["query"], encoding="ascii")
        resp = await self._get_or_post(self.search_url, params=params)
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

        # params = {"query": quote(query)}
        params = {"query": query}
        resp = await self._get(self.report_url, params=params)
        return resp


class DiffbotEnhanceClient(BaseDiffbotKGClient):
    """
    A client for interacting with the Diffbot Enhance API.

    This client provides methods for enhancing content using the Diffbot Enhance API,
    managing bulk jobs, and retrieving job results and coverage reports.
    """

    enhance_url = BaseDiffbotKGClient.url / "enhance"
    enhance_bulk_url = enhance_url / "bulk"
    bulk_status_url = enhance_bulk_url / "status"
    single_bulkjob_result_url = enhance_bulk_url / "{bulkjobId}/{jobIdx}"
    bulk_job_results_url = enhance_bulk_url / "{bulkjobId}"
    bulk_job_coverage_report_url = enhance_bulk_url / "{bulkjobId}/coverage/{reportId}"
    bulk_job_stop_url = enhance_bulk_url / "{bulkjobId}/stop"

    param_keys = BaseDiffbotKGClient.param_keys + ["refresh", "search", "useCache"]

    async def enhance(self, params) -> DiffbotResponse:
        """
        Enhance content using the Diffbot Enhance API.

        Args:
            params (dict): The parameters for enhancing the content.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        resp = await self._get(self.enhance_url, params=params)
        return resp

    async def create_bulkjob(self, params) -> DiffbotResponse:
        """
        Create a bulk job for enhancing multiple content items.

        Args:
            params (dict): The parameters for creating the bulk job.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        resp = await self._post(self.enhance_bulk_url, params=params)
        return resp

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
