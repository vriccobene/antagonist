import unittest
import requests
import json

URL = "http://localhost:8000/api/v1/label-store/anomaly/"
HEADERS = {
    'Content-Type': 'application/json'
}


# TODO Need to finalise the tests


# Updated for Anomaly API
class AnomalyAPITestCase(unittest.TestCase):

    def setUp(self):
        # Common payload for POST requests to Anomaly API
        self.valid_payload = {
            "description": "Connectivity seems to go down",
            "start_time": "2025-08-30T10:20:30.400+02:30",
            "end_time": "2025-08-30T10:21:30.400+02:30",
            "confidence_score": 0.6,
            "annotator": {
                "name": "Antagonist-Detector",
                "annotator_type": "algorithm"
            },
            "symptom": {
                "concern_score": 0.3,
            }
        }

    def test_post_anomaly_success(self):
        payload = json.dumps(self.valid_payload)
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [200, 201])

    def test_post_anomaly_missing_required_field(self):
        payload = json.dumps({
            # "start_time" is missing
            # "start_time": "2025-08-30T10:20:30.400+02:30",
            "end_time": "2025-08-30T10:21:30.400+02:30",
            "confidence_score": 0.6,
            "annotator": {
                "name": "Antagonist-Detector",
                "annotator_type": "algorithm"
            },
            "symptom": {
                "concern_score": 0.3
            }
        })
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [400, 422])

    def test_post_anomaly_invalid_confidence_score(self):
        payload = json.dumps({
            "description": "Invalid confidence",
            "start_time": "2025-08-30T10:20:30.400+02:30",
            "end_time": "2025-08-30T10:21:30.400+02:30",
            "confidence_score": 2.0,  # Invalid, should be <= 1.0
            "annotator": {
                "name": "Antagonist-Detector",
                "annotator_type": "algorithm"
            },
            "symptom": {
                "concern_score": 0.3
            }
        })
        response = requests.post(URL, headers=HEADERS, data=payload)
        self.assertIn(response.status_code, [400, 422])

    # This is currently not supported.
    # def test_post_multiple_anomalies(self):
    #     # Assuming the API supports bulk creation (list of anomalies)
    #     payload = json.dumps([
    #         {
    #             "description": "Connectivity seems to go down",
    #             "start_time": "2025-08-30T10:20:30.400+02:30",
    #             "end_time": "2025-08-30T10:21:30.400+02:30",
    #             "confidence_score": 0.6,
    #             "annotator": {
    #                 "name": "Antagonist-Detector",
    #                 "annotator_type": "algorithm"
    #             },
    #             "symptom": {
    #                 "concern_score": 0.3
    #             }
    #         },
    #         {
    #             "description": "Interface flapping",
    #             "start_time": "2025-08-30T10:21:30.400+02:30",
    #             "end_time": "2025-08-30T10:22:30.400+02:30",
    #             "confidence_score": 0.6,
    #             "annotator": {
    #                 "name": "Antagonist-Detector",
    #                 "annotator_type": "algorithm"
    #             },
    #             "symptom": {
    #                 "concern_score": 0.6
    #             }
    #         },
    #         {
    #             "description": "Network Node is no more reachable",
    #             "start_time": "2025-08-30T10:22:30.400+02:30",
    #             "end_time": "2025-08-30T10:23:30.400+02:30",
    #             "confidence_score": 0.6,
    #             "annotator": {
    #                 "name": "Antagonist-Detector",
    #                 "annotator_type": "algorithm"
    #             },
    #             "symptom": {
    #                 "concern_score": 0.9
    #             }
    #         }
    #     ])
    #     response = requests.post(URL, headers=HEADERS, data=payload)
    #     self.assertIn(response.status_code, [200, 201])

    def test_get_anomaly_returns_posted_anomaly(self):
        # First, POST a valid anomaly
        post_response = requests.post(
            URL, headers=HEADERS,
            params={json.dumps(self.valid_payload)})
        self.assertIn(post_response.status_code, [200, 201])
        # Then, GET the anomalies
        get_response = requests.get(URL, headers=HEADERS)
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        # Check that at least one item matches the posted description
        self.assertTrue(any(
            item.get("description") == self.valid_payload["description"]
            for item in data))

    def test_get_anomaly_empty(self):
        # Assuming the store can be empty (e.g., after a reset)
        get_response = requests.get(URL, headers=HEADERS)
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        self.assertIsInstance(data, list)

    def test_get_anomaly_with_query_params(self):
        # POST an anomaly with a unique description
        unique_description = "Unique Anomaly 12345"
        payload = self.valid_payload.copy()
        payload['anomaly_filters'] = {}
        payload['anomaly_filters']["description"] = unique_description
        post_response = requests.post(URL, headers=HEADERS, data=json.dumps(
            payload))
        self.assertIn(post_response.status_code, [200, 201])
        # GET with query params (assuming API supports filtering by
        # description)
        get_response = requests.get(URL, headers=HEADERS, params={
            "anomaly_filters": {"description": unique_description}})
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        self.assertTrue(any(
            item.get("description") == unique_description 
            for item in data))

    def test_post_anomaly_invalid_json(self):
        # Send invalid JSON
        invalid_json = '{"description": "Broken JSON", ' \
                       '"start_time": "2025-08-30T10:20:30"'
        response = requests.post(URL, headers=HEADERS, data=invalid_json)
        self.assertIn(response.status_code, [400, 422])


if __name__ == "__main__":
    unittest.main()
