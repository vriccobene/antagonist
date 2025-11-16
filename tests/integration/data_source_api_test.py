
import unittest
import requests
import json
from sqlmodel import Session, select
from antagonist_label_store.src.backend.db.database import engine
from antagonist_label_store.src.backend.data_models.telemetry.db import (
    DataSource)

URL = "http://localhost:8000/api/v1/telemetry/data-source/"
HEADERS = {
    'Content-Type': 'application/json'
}


# Adapted to test DataSource API
class DataSourceAPITestCase(unittest.TestCase):
    def tearDown(self):
        # Directly delete test data sources from the DB
        with Session(engine) as session:
            # Delete all data sources with names used in tests
            names_to_delete = [
                "Test DataSource", "DS1", "DS2", "DS3", "Invalid Endpoint", "UniqueDS12345", "Broken JSON"
            ]
            for name in names_to_delete:
                sources = session.exec(select(DataSource).where(DataSource.name == name)).all()
                for ds in sources:
                    session.delete(ds)
            session.commit()

    def setUp(self):
        # Common payload for POST requests to DataSource API (updated schema)
        self.valid_payload = {
            "name": "Test DataSource",
            "description": "A test datasource for integration testing",
            "type": {
                "database": "influxdb",
                "version": "1.0.0"
            },
            "end_point": {
                "url": "http://localhost:5432",
                "metadata": {"description": "Main DB endpoint"}
            }
        }

    def test_post_datasource_success(self):
        payload = json.dumps(self.valid_payload)
        response = requests.post(URL, headers=HEADERS, data=payload)
        print("Response:", response.status_code, response.text)
        self.assertIn(response.status_code, [200, 201])

    def test_post_datasource_missing_required_field(self):
        payload = json.dumps({
            # "name" is missing
            "description": "Missing name field",
            "type": {
                "database": "influxdb",
                "version": "1.0.0"
            },
            "end_point": {
                "url": "http://localhost:5432",
                "metadata": {"description": "Main DB endpoint"}
            }
        })
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_post_datasource_invalid_endpoint(self):
        payload = json.dumps({
            "name": "Invalid Endpoint",
            "description": "Invalid endpoint",
            "type": {
                "database": "influxdb",
                "version": "1.0.0"
            },
            "end_point": {
                # URL is missing which is required
            }
        })
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_get_datasource_returns_posted_datasource(self):
        # First, POST a valid datasource
        post_response = requests.post(URL, headers=HEADERS, data=json.dumps(self.valid_payload))
        self.assertIn(post_response.status_code, [200, 201])
        # Then, GET the datasources
        get_response = requests.get(URL, headers=HEADERS)
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        # Check that at least one item matches the posted name
        self.assertTrue(any(item.get("name") == self.valid_payload["name"] for item in data))

    def test_get_datasource_empty(self):
        # Assuming the store can be empty (e.g., after a reset)
        get_response = requests.get(URL, headers=HEADERS)
        print("GET Response:", get_response.status_code, get_response.text)
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        self.assertIsInstance(data, list)

    def test_get_datasource_with_query_params(self):
        # POST a datasource with a unique name
        unique_name = "UniqueDS12345"
        payload = self.valid_payload.copy()
        payload["name"] = unique_name
        post_response = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
        self.assertIn(post_response.status_code, [200, 201])
        # GET with query params (assuming API supports filtering by name)
        get_response = requests.get(URL, headers=HEADERS, params={"name": unique_name})
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        self.assertTrue(any(item.get("name") == unique_name for item in data))

    def test_post_datasource_invalid_json(self):
        # Send invalid JSON
        invalid_json = '{"name": "Broken JSON", "type": {"database": "influxdb", "version": "1.0.0"}'
        response = requests.post(URL, headers=HEADERS, data=invalid_json)
        self.assertIn(response.status_code, [400, 422])


if __name__ == "__main__":
    unittest.main()
