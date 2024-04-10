from diffbot_kg.models.response.base import BaseJsonLinesDiffbotResponse


class DiffbotListBulkJobsResponse(BaseJsonLinesDiffbotResponse):
    """DiffbotBulkJobListResponse represents the status of a Diffbot Enhance
    API List BulkJobs for Token API request.

    It contains the response status, headers, and JSON content.

    The create classmethod is the main constructor, which handles converting
    an aiohttp response into a DiffbotResponse.
    """

    pass
