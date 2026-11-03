import pytest

from framework.pages.saucedemo_login_page import SaucedemoLoginPage


class BaseUITest:
    """Base class for all UI tests. Injects page and pre-built page objects via autouse fixture."""

    @pytest.fixture(autouse=True)
    def _setup(self, page):
        self.page = page
        self.login_page = SaucedemoLoginPage(page)
        yield
