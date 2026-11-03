import os

import allure  # type: ignore[import-untyped]
import pytest
from playwright.sync_api import expect

from framework.support.base_ui_test import BaseUITest
from framework.utils.step_decorator import step


@allure.feature("Authentication")
@pytest.mark.login_and_product_page
class TestSaucedemoLoginAndShopping(BaseUITest):
    @allure.title("Standard user can log in successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Standard user login")
    @allure.tag("Smoke", "Login")
    def test_validate_standard_user_login(self):
        with step("Log in as standard user"):
            self.login_page.login(
                os.environ["STANDARD_USERNAME"],
                os.environ["PASSWORD"],
            )
        with step("Assert app logo is visible after login"):
            expect(self.page.locator(".app_logo")).to_be_visible()

    @allure.title("Locked-out user sees an error message")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Locked-out user login")
    @allure.tag("Negative")
    @pytest.mark.negative_test
    def test_validate_locked_out_user_login(self):
        with step("Attempt login as locked-out user"):
            self.login_page.login(
                os.environ["LOCKED_OUT_USER"],
                os.environ["PASSWORD"],
            )
        with step("Assert locked-out error message is displayed"):
            expect(self.page.get_by_role("alert")).to_have_text(
                "Epic sadface: Sorry, this user has been locked out."
            )
