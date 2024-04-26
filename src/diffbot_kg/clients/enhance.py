from typing import cast

from diffbot_kg.clients.base import BaseDiffbotKGClient
from diffbot_kg.models.response import (
    DiffbotBulkJobCreateResponse,
    DiffbotBulkJobStatusResponse,
    DiffbotCoverageReportResponse,
    DiffbotEntitiesResponse,
    DiffbotListBulkJobsResponse,
)
from diffbot_kg.models.response.bulkjob_results import DiffbotBulkJobResultsResponse


class DiffbotEnhanceClient(BaseDiffbotKGClient):
    """
    A client for interacting with the Diffbot Enhance API.

    This client provides methods for enhancing content using the Diffbot Enhance API,
    managing bulk jobs, and retrieving job results and coverage reports.
    """

    enhance_url = BaseDiffbotKGClient.url / "enhance"
    bulk_job_url = enhance_url / "bulk"
    list_bulk_jobs_url = bulk_job_url / "status"
    bulk_job_status_url = bulk_job_url / "{bulkjobId}" / "status"
    bulk_job_results_url = bulk_job_url / "{bulkjobId}"
    bulk_job_single_result_url = bulk_job_results_url / "{jobIdx}"
    bulk_job_coverage_report_url = bulk_job_url / "report/{bulkjobId}/{reportId}"
    bulk_job_stop_url = bulk_job_url / "{bulkjobId}/stop"

    async def enhance(self, params) -> DiffbotEntitiesResponse:
        """
        Enhance content using the Diffbot Enhance API.

        Args:
            params (dict): The parameters for enhancing the content.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        resp = await self._get(self.enhance_url, params=params)
        resp.__class__ = DiffbotEntitiesResponse
        return cast(DiffbotEntitiesResponse, resp)

    async def create_bulkjob(
        self, json: list[dict], params=None
    ) -> DiffbotBulkJobCreateResponse:
        """
        Create a bulk job for enhancing multiple content items.

        Args:
            data (list[dict]): The content items to enhance.
            params (dict): The parameters for creating the bulk job.

        Returns:
            DiffbotBulkJobResponse: The response from the Diffbot API.
        """

        if json is None or not json:
            raise ValueError("data must be provided")

        resp = await self._post(self.bulk_job_url, params=params, json=json)
        resp.__class__ = DiffbotBulkJobCreateResponse
        return cast(DiffbotBulkJobCreateResponse, resp)

    async def bulkjob_status(self, bulkjobId: str) -> DiffbotBulkJobStatusResponse:
        """
        Poll the status of an Enhance Bulkjob by its ID.

        Args:
            bulkjobId (str): The ID of the bulk job.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        url = self.bulk_job_status_url.human_repr().format(bulkjobId=bulkjobId)
        resp = await self._get(url)
        resp.__class__ = DiffbotBulkJobStatusResponse
        return cast(DiffbotBulkJobStatusResponse, resp)

    async def list_bulkjobs(self) -> DiffbotListBulkJobsResponse:
        """
        Poll the status of all Enhance Bulkjobs for a token.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        resp = await self._get(self.list_bulk_jobs_url)
        resp.__class__ = DiffbotListBulkJobsResponse
        return cast(DiffbotListBulkJobsResponse, resp)

    async def bulkjob_results(self, bulkjobId: str) -> DiffbotBulkJobResultsResponse:
        """
        Download the results of a completed Enhance Bulkjob by its ID.

        Args:
            bulkjobId (str): The ID of the bulk job.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        url = self.bulk_job_results_url.human_repr().format(bulkjobId=bulkjobId)
        resp = await self._get(url)
        resp.__class__ = DiffbotBulkJobResultsResponse
        return cast(DiffbotBulkJobResultsResponse, resp)

    async def bulkjob_coverage_report(
        self, bulkjobId: str, reportId: str
    ) -> DiffbotCoverageReportResponse:
        """
        Download the coverage report of a completed Enhance Bulkjob by its ID and report ID.

        Args:
            bulkjobId (str): The ID of the bulk job.
            reportId (str): The ID of the report.

        Returns:
            DiffbotResponse: The response from the Diffbot API.
        """

        url = self.bulk_job_coverage_report_url.human_repr().format(
            bulkjobId=bulkjobId, reportId=reportId
        )

        resp = await self._get(url)
        resp.__class__ = DiffbotCoverageReportResponse
        return cast(DiffbotCoverageReportResponse, resp)

    async def single_bulkjob_result(
        self,
        bulkjobId: str,
        jobIdx: int,
    ) -> DiffbotEntitiesResponse:
        """
        Download the result of a single job within a bulkjob by specifying the index of the job.

        Args:
            bulkjobId (str): The ID of the bulk job.
            jobIdx (int): The index of the job within the bulk job.

        Returns:
            DiffbotEntitiesResponse: The response from the Diffbot API.
        """

        url = self.bulk_job_single_result_url.human_repr().format(
            bulkjobId=bulkjobId, jobIdx=jobIdx
        )
        resp = await self._get(url)
        resp.__class__ = DiffbotEntitiesResponse
        return cast(DiffbotEntitiesResponse, resp)

    async def stop_bulkjob(
        self,
        bulkJobId: str,
    ) -> DiffbotBulkJobStatusResponse:
        """
        Stop an active Enhance Bulkjob by its ID.

        Args:
            bulkjobId (str): The ID of the bulk job.

        Returns:
            DiffbotEntitiesResponse: The response from the Diffbot API.
        """

        url = self.bulk_job_stop_url.human_repr().format(bulkjobId=bulkJobId)
        resp = await self._get(url)
        resp.__class__ = DiffbotBulkJobStatusResponse
        return cast(DiffbotBulkJobStatusResponse, resp)
