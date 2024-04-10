from diffbot_kg.models.response.base import BaseJsonDiffbotResponse


class DiffbotBulkJobStatusResponse(BaseJsonDiffbotResponse):
    """DiffbotBulkJobStatusResponse represents the status of a Diffbot Enhance BulkJob.

    It contains the response status, headers, and JSON content. Provides
    convenience properties to access the 'jobId' key from the content

    The create classmethod is the main constructor, which handles converting
    an aiohttp response into a DiffbotResponse.
    """

    @property
    def jobId(self) -> str:
        return self.content["content"]["job_id"]

    @property
    def complete(self) -> str:
        return self.content["content"]["status"] == "COMPLETE"

    @property
    def reports(self):
        return self.content["content"]["reports"]
