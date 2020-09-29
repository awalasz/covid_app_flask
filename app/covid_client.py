import logging
from urllib.parse import urljoin

import requests


class CovidRestClient(requests.Session):
    def __init__(self, base_url="https://api.covid19api.com/", **kwargs):
        self.logger = kwargs.pop("logger", logging.getLogger("restclients"))
        self.base_url = base_url
        super().__init__()

    def request(
        self, method: str, path: str, *args, **kwargs
    ) -> requests.models.Response:
        """Underlying method performing HTTP request."""
        url = urljoin(self.base_url, path)
        response = super().request(method, url, *args, **kwargs)
        self.logger.debug(
            "Received %s status code from %s", response.status_code, response.url,
        )
        if not response.ok:
            self.logger.debug("Response body: %s", response.text)
        return response
