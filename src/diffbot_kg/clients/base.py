from typing import Any, Self

from yarl import URL

from diffbot_kg.clients.session import BaseDiffbotResponse, DiffbotSession


class BaseDiffbotKGClient:
    """
    Base class for Diffbot Knowledge Graph API clients.
    """

    url = URL("https://kg.diffbot.com/kg/v3/")

    def __init__(self, token: str, **default_params: Any) -> None:
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
        self._session = DiffbotSession()

    def _merge_params(self, params: dict[str, Any] | None) -> dict[str, Any]:
        """
        Merges the given parameters with the default parameters.

        Args:
            params (dict): The parameters to merge.

        Returns:
            dict: The merged parameters.
        """

        params = params or {}
        params = {**self.default_params, **params}

        return {k: v for k, v in params.items() if v is not None}

    async def _get(
        self, url: str | URL, params: dict | None = None, headers: dict | None = None
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

        return await self._session.get(url, params=params, headers=headers)

    async def _post(
        self,
        url: str | URL,
        params: dict | None = None,
        json: dict | list[dict] | None = None,
        headers: dict | None = None,
    ) -> BaseDiffbotResponse:
        """
        Sends a POST request to the Diffbot API.

        Args:
            url (str | URL): The URL to send the request to.
            params (dict, optional): The query parameters for the request. Defaults to None.
            json (dict | list[dict], optional): The JSON data for the request body. Defaults to None.

        Returns:
            BaseDiffbotResponse: The response from the API.
        """

        params = self._merge_params(params)

        headers = {
            "content-type": "application/json",
            **(headers or {}),
        }

        return await self._session.post(url, params=params, headers=headers, json=json)

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

        if url_len <= 3000:
            return await self._session.get(url, params=params, headers={})
        else:
            token = params.pop("token", None) if params else None
            json, params = params, {"token": token}
            headers = {"content-type": "application/json"}
            return await self._session.post(
                url, params=params, headers=headers, json=json
            )

    async def close(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
