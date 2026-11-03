import time

import allure  # type: ignore[import-untyped]
import pytest

from framework.support.base_api_test import BaseAPITest
from framework.testdata.pet_payload import new_pet_payload, pet_id
from framework.utils.api_helper import attach_api_response
from framework.utils.step_decorator import step


@allure.feature("Petstore API")
@allure.story("Pet CRUD lifecycle")
@pytest.mark.incremental
class TestPetstoreApiCrudLifecycle(BaseAPITest):
    @allure.title("Auth: Verify API key is authorised")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("Auth", "API")
    def test_auth_verify_api_key_authorized(self):
        with step("GET /pet/findByStatus → assert 200 OK"):
            response = self.client.verify_auth()
            attach_api_response(response.url, response.json())
            assert response.ok
            assert response.status == 200

    @allure.title("POST: Create a new pet")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("CRUD", "API")
    def test_post_create_new_pet(self):
        with step("POST /pet → assert pet created with correct fields"):
            response = self.client.create_pet(new_pet_payload)
            pet = response.json()
            attach_api_response(response.url, pet)
            assert response.ok
            assert response.status == 200
            assert pet["id"] == pet_id
            assert pet["name"] == new_pet_payload["name"]
            assert pet["status"] == new_pet_payload["status"]

    @allure.title("GET: Retrieve and validate the created pet")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("CRUD", "API")
    def test_get_retrieve_and_validate_created_pet(self):
        pet = None
        response_url = ""

        with step("Poll GET /pet/{id} until available (max 30 s)"):
            deadline = time.time() + 30
            while time.time() < deadline:
                response = self.client.get_pet(pet_id)
                response_url = response.url
                if response.ok:
                    pet = response.json()
                    break
                time.sleep(2)

        assert pet is not None, f"Pet {pet_id} was not available within 30 seconds"
        attach_api_response(response_url, pet)

        with step("Assert retrieved pet matches created payload"):
            assert pet["id"] == pet_id
            assert pet["name"] == new_pet_payload["name"]
            assert pet["status"] == new_pet_payload["status"]
            assert pet["category"]["name"] == new_pet_payload["category"]["name"]

    @allure.title("DELETE: Remove the pet and confirm deletion")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("CRUD", "API")
    def test_delete_remove_pet_and_confirm_deletion(self):
        with step("DELETE /pet/{id} → assert OK"):
            delete_response = self.client.delete_pet(pet_id)
            attach_api_response(delete_response.url, delete_response.json())
            assert delete_response.ok

        with step("GET /pet/{id} → assert 404 after deletion"):
            get_response = self.client.get_pet(pet_id)
            assert get_response.status == 404
