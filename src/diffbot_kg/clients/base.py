from typing import Any

from yarl import URL

from diffbot_kg.clients.session import BaseDiffbotResponse, DiffbotSession


class BaseDiffbotKGClient:
    """
    Base class for Diffbot Knowledge Graph API clients.
    """

    url = URL("https://kg.diffbot.com/kg/v3/")

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

        # sourcery skip: inline-immediately-returned-variable
        params = {k: v for k, v in params.items() if v is not None}
        return params

    async def _get(
        self, url: str | URL, params=None, headers=None
    ) -> BaseDiffbotResponse:
        """
        Sends a GET request to the Diffbot API.

        Args:
            url (str | URL): The URL to send the request to.
            params (dict, optional): The query parameters for the request. Defaults to None.
            headers (dict, optional): The headers for the request. Defaults to None.

        Returns:
            BaseDiffbotResponse: The response from the API.
        """

        headers = headers or {}

        params = self._merge_params(params)

        # sourcery skip: inline-immediately-returned-variable
        resp = await self.s.get(url, params=params, headers=headers)
        return resp

    async def _post(
        self,
        url: str | URL,
        params: dict | None = None,
        json: dict | list[dict] | None = None,
        headers=None,
    ) -> BaseDiffbotResponse:
        """
        Sends a POST request to the Diffbot API.

        Args:
            url (str | URL): The URL to send the request to.
            params (dict, optional): The query parameters for the request. Defaults to None.
            data (dict, optional): The data for the request body. Defaults to None.

        Returns:
            BaseDiffbotResponse: The response from the API.
        """

        params = self._merge_params(params)

        headers = {
            "content-type": "application/json",
            **(headers or {}),
        }

        # sourcery skip: inline-immediately-returned-variable
        resp = await self.s.post(url, params=params, headers=headers, json=json)
        return resp

    async def _get_or_post(
        self, url: str | URL, params: dict | None = None
    ) -> BaseDiffbotResponse:
        """
        Sends a GET or POST request to the Diffbot API, depending on the length of the URL.

        Args:
            url (str | URL): The URL to send the request to.
            params (dict, optional): The query parameters for the request. Defaults to None.

        Returns:
            BaseDiffbotResponse: The response from the API.
        """

        params = self._merge_params(params)

        url_len = len(bytes(str(url % params), encoding="ascii"))

        # sourcery skip: remove-unnecessary-else
        if url_len <= 3000:
            return await self._get(url, params=params)
        else:
            token = params.pop("token", None) if params else None
            json, params = params, {"token": token}
            return await self._post(url, params=params, json=json)

    async def close(self):
        await self.s.close()
