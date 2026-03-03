from diffbot_kg.models.response.base import BaseJsonDiffbotResponse


class DiffbotEntitiesResponse(BaseJsonDiffbotResponse):
    """DiffbotQueryResponse represents the response from a Diffbot API request
    containing a list of entities.

    It contains the response status, headers, and JSON content. Provides
    convenience properties to access the 'data' and 'entities' portions
    of the JSON content.

    The create classmethod is the main constructor, which handles converting
    an aiohttp response into a DiffbotResponse.
    """

    @property
    def data(self) -> list[dict]:
        return self.content["data"]

    @property
    def entities(self) -> list[dict]:
        # Note: this class/method will not be compatible with facet queries
        # (no entities returned)
        return [d["entity"] for d in self.data]
