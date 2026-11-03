from playwright.sync_api import Page

from framework.utils.step_decorator import step


class SaucedemoLoginPage:
    def __init__(self, page: Page):
        self.page = page

    @property
    def username_field(self):
        return self.page.get_by_label("Username")

    @property
    def password_field(self):
        return self.page.get_by_label("Password")

    @property
    def login_button(self):
        return self.page.locator("[data-test='login-button']")

    @property
    def locked_out_user_alert(self):
        return self.page.get_by_role("alert")

    @step("Navigate to login page and submit credentials")
    def login(self, username: str, password: str) -> None:
        self.page.goto("/")
        self.username_field.fill(username)
        self.password_field.fill(password)
        self.login_button.click()
