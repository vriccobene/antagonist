import unittest
import requests
import json

URL = "http://localhost:8000/api/v1/label-store/relevant-state/"
HEADERS = {
    'Content-Type': 'application/json'
}


# TODO Need to finalise the tests

class RelevantStateAPITestCase(unittest.TestCase):

    def setUp(self):
        # Common payload for POST requests
        self.valid_payload = {
            "description": "August Incident",
            "start_time": "2025-08-30T10:20:30",
            "end_time": "2025-08-31T13:20:30",
            "state": "confirmed",
            "confidence_score": 0.9,
            "concern_score": 0.8,
            "publisher": {
                "name": "Antagonist-Detector",
                "version": "1.0.0"
            },
            "service": {},
            "anomaly": [
                {
                    "description": "Connectivity seems to go down",
                    "start_time": "2025-08-30T10:20:30.400+02:30",
                    "end_time": "2025-08-30T10:21:30.400+02:30",
                    "confidence_score": 0.6,
                    "annotator": {
                        "name": "Antagonist-Detector",
                        "annotator_type": "algorithm"
                    },
                    "symptom": {
                        "concern_score": 0.3
                    }
                }
            ]
        }

    def test_post_relevant_state_success(self):
        payload = json.dumps(self.valid_payload)
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [200, 201])

    def test_post_relevant_state_missing_required_field(self):
        payload = json.dumps({
            # "description" is missing
            "start_time": "2025-08-30T10:20:30",
            "end_time": "2025-08-31T13:20:30",
            "state": "confirmed",
            "confidence_score": 0.9,
            "concern_score": 0.8,
            "publisher": {
                "name": "Antagonist-Detector",
                "version": "1.0.0"
            },
            "service": {},
            "anomaly": []
        })
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_post_relevant_state_invalid_confidence_score(self):
        payload = json.dumps({
            "description": "Invalid confidence",
            "start_time": "2025-08-30T10:20:30",
            "end_time": "2025-08-31T13:20:30",
            "state": "confirmed",
            "confidence_score": 2.0,  # Invalid, should be <= 1.0
            "concern_score": 0.8,
            "publisher": {
                "name": "Antagonist-Detector",
                "version": "1.0.0"
            },
            "service": {},
            "anomaly": []
        })
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_post_relevant_state_multiple_anomalies(self):
        payload = json.dumps({
            "description": "August Incident",
            "start_time": "2025-08-30T10:20:30",
            "end_time": "2025-08-31T13:20:30",
            "state": "confirmed",
            "confidence_score": 0.9,
            "concern_score": 0.8,
            "publisher": {
                "name": "Antagonist-Detector",
                "version": "1.0.0"
            },
            "service": {},
            "anomaly": [
                {
                    "description": "Connectivity seems to go down",
                    "start_time": "2025-08-30T10:20:30.400+02:30",
                    "end_time": "2025-08-30T10:21:30.400+02:30",
                    "confidence_score": 0.6,
                    "annotator": {
                        "name": "Antagonist-Detector",
                        "annotator_type": "algorithm"
                    },
                    "symptom": {
                        "concern_score": 0.3
                    }
                },
                {
                    "description": "Interface flapping",
                    "start_time": "2025-08-30T10:21:30.400+02:30",
                    "end_time": "2025-08-30T10:22:30.400+02:30",
                    "confidence_score": 0.6,
                    "annotator": {
                        "name": "Antagonist-Detector",
                        "annotator_type": "algorithm"
                    },
                    "symptom": {
                        "concern_score": 0.6
                    }
                },
                {
                    "description": "Network Node is no more reachabel",
                    "start_time": "2025-08-30T10:22:30.400+02:30",
                    "end_time": "2025-08-30T10:23:30.400+02:30",
                    "confidence_score": 0.6,
                    "annotator": {
                        "name": "Antagonist-Detector",
                        "annotator_type": "algorithm"
                    },
                    "symptom": {
                        "concern_score": 0.9
                    }
                }
            ]
        })
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [200, 201])

    def test_get_relevant_state_returns_posted_state(self):
        # First, POST a valid state
        post_response = requests.post(URL, headers=HEADERS, data=json.dumps(self.valid_payload))
        self.assertIn(post_response.status_code, [200, 201])
        # Then, GET the states
        get_response = requests.get(URL, headers=HEADERS)
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        # Check that at least one item matches the posted description
        self.assertTrue(any(item.get("description") == self.valid_payload["description"] for item in data))

    def test_get_relevant_state_empty(self):
        # Assuming the store can be empty (e.g., after a reset)
        # This test may need to be adjusted if the store always has data
        get_response = requests.get(URL, headers=HEADERS)
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        self.assertIsInstance(data, list)

    def test_get_relevant_state_with_query_params(self):
        # POST a state with a unique description
        unique_description = "Unique Incident 12345"
        payload = self.valid_payload.copy()
        payload["description"] = unique_description
        post_response = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
        self.assertIn(post_response.status_code, [200, 201])
        # GET with query params (assuming API supports filtering by description)
        get_response = requests.get(URL, headers=HEADERS, params={"description": unique_description})
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        self.assertTrue(any(item.get("description") == unique_description for item in data))

    def test_post_relevant_state_invalid_json(self):
        # Send invalid JSON
        invalid_json = '{"description": "Broken JSON", "start_time": "2025-08-30T10:20:30"'
        response = requests.post(URL, headers=HEADERS, data=invalid_json)
        self.assertIn(response.status_code, [400, 422])


if __name__ == "__main__":
    unittest.main()
