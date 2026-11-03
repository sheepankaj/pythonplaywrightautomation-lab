from playwright.sync_api import APIRequestContext, APIResponse

from framework.utils.step_decorator import step


class PetStoreClient:
    def __init__(self, api_context: APIRequestContext):
        self._api = api_context

    @step("Verify API key is authorised (GET /pet/findByStatus)")
    def verify_auth(self) -> APIResponse:
        return self._api.get("pet/findByStatus", params={"status": "available"})

    @step("Create new pet (POST /pet)")
    def create_pet(self, payload: dict) -> APIResponse:
        return self._api.post("pet", data=payload)

    @step("Retrieve pet by ID (GET /pet/{id})")
    def get_pet(self, pet_id: int) -> APIResponse:
        return self._api.get(f"pet/{pet_id}")

    @step("Delete pet by ID (DELETE /pet/{id})")
    def delete_pet(self, pet_id: int) -> APIResponse:
        return self._api.delete(f"pet/{pet_id}")
