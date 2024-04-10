from diffbot_kg.models.response.base import BaseJsonDiffbotResponse


class DiffbotBulkJobCreateResponse(BaseJsonDiffbotResponse):
    """DiffbotResponse represents the response from a Diffbot BulkJob API request.

    It contains the response status, headers, and JSON content. Provides
    convenience properties to access the 'jobId' key from the content

    The create classmethod is the main constructor, which handles converting
    an aiohttp response into a DiffbotResponse.
    """

    @property
    def jobId(self) -> str:
        return self.content["job_id"]
