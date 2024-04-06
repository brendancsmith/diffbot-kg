import contextlib

from diffbot_kg.models.response.base import BaseJsonLinesDiffbotResponse


class DiffbotBulkJobResultsResponse(BaseJsonLinesDiffbotResponse):
    """DiffbotBulkJobResultsResponse represents the status of a Diffbot Enhance BulkJob.

    It contains the response status, headers, and JSON content. Provides
    convenience properties to access the 'jobId' key from the content

    The create classmethod is the main constructor, which handles converting
    an aiohttp response into a DiffbotResponse.
    """

    @property
    def jobId(self) -> str:
        for query in self.content:
            with contextlib.suppress(KeyError):
                return query["request_ctx"]["query_ctx"]["bulkjobId"]

        raise RuntimeError("No bulkJobId found in the response")

    @property
    def reportId(self) -> str:
        return self.headers["X-Diffbot-ReportId"]

    @property
    def entities(self):
        return [data["entity"] for result in self.content for data in result["data"]]
