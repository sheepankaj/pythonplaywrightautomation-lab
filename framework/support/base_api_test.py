import pytest
from playwright.sync_api import Playwright

from framework.api.petstore_client import PetStoreClient
from framework.utils.auth_helper import get_api_auth_headers


class BaseAPITest:
    """Base class for all API tests. Creates a scoped APIRequestContext and PetStoreClient."""

    @pytest.fixture(autouse=True)
    def _setup_api(self, playwright: Playwright):
        api_context = playwright.request.new_context(
            base_url="https://petstore.swagger.io/v2/",
            extra_http_headers=get_api_auth_headers(),
        )
        self.client = PetStoreClient(api_context)
        yield
        api_context.dispose()
