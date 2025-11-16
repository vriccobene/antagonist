import unittest
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/telemetry/monitored-entity-type"
HEADERS = {'Content-Type': 'application/json'}


class MonitoredEntityTypeAPITestCase(unittest.TestCase):

    def setUp(self):
        # Create a DataSource for testing
        data_source_payload = {
            "name": "Test DataSource",
            "description": "Created for monitored entity type tests",
            "type": {
                "database": "influxdb",
                "version": "str"
            },
            "end_point": {
                "url": "http://localhost:1234",
                "method": "GET"
            }
        }
        ds_response = requests.post(
            "http://localhost:8000/api/v1/telemetry/data-source/", 
            headers=HEADERS,
            data=json.dumps(data_source_payload)
        )
        self.assertIn(ds_response.status_code, [200, 201])
        self.data_source_id = ds_response.json()["id"] if isinstance(ds_response.json(), dict) else ds_response.json()
        self.create_payload = {
            "name": "L3VPN",
            "description": "L3VPN Connectivity Service",
            "data_source_id": self.data_source_id
        }
        self.update_payload = {
            "name": "L3VPN - Updated",
            "description": "L3VPN Connectivity Service",
            "data_source_id": self.data_source_id
        }

    def tearDown(self):
        # Delete the DataSource after each test
        if hasattr(self, "data_source_id") and self.data_source_id:
            requests.delete(
                f"http://localhost:8000/api/v1/telemetry/data-source/{self.data_source_id}",
                headers=HEADERS
            )

    def test_get_monitored_entity_types(self):
        response = requests.get(BASE_URL, headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        # Optionally check response content

    def test_post_monitored_entity_type(self):
        response = requests.post(
            BASE_URL + "/",
            headers=HEADERS,
            data=json.dumps(self.create_payload))
        self.assertIn(response.status_code, [200, 201])
        # Save the created ID for update test
        self.created_id = response.json() \
            if isinstance(response.json(), str) \
            else response.json().get("id")
        self.assertIsNotNone(self.created_id)

    def test_put_monitored_entity_type(self):
        # First, create an entity to update
        post_response = requests.post(
            BASE_URL + "/",
            headers=HEADERS,
            data=json.dumps(self.create_payload))
        self.assertIn(post_response.status_code, [200, 201])
        entity_id = post_response.json() \
            if isinstance(post_response.json(), str) \
            else post_response.json().get("id")
        self.assertIsNotNone(entity_id)

        # Now, update it
        put_url = f"{BASE_URL}/{entity_id}"
        put_response = requests.put(put_url, headers=HEADERS, data=json.dumps(self.update_payload))
        self.assertEqual(put_response.status_code, 200)
        # Optionally check response content


if __name__ == "__main__":
    unittest.main()
