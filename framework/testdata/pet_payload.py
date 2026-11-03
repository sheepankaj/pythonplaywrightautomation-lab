import time

pet_id = int(time.time())

new_pet_payload = {
    "id": pet_id,
    "name": "TestDoggo",
    "status": "available",
    "photoUrls": ["https://example.com/testdog.jpg"],
    "category": {"id": 1, "name": "Dogs"},
    "tags": [{"id": 1, "name": "test"}],
}
