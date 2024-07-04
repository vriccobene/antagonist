# import torch
# import random
# import numpy as np
# import pandas as pd


# # Set the seed for reproduceabilty
# torch.manual_seed(0)
# torch.use_deterministic_algorithms(True)
# random.seed(0)
# np.random.seed(0)


# import datetime
import pandas as pd


import sys
# sys.path.append("./../")
# import service



## Loading ML model

import os
import time
import pathlib
import datetime
from demo_anomaly_detector import core


DEMO_FOLDER = pathlib.Path(".").resolve().parent.parent
DATA_FOLDER = DEMO_FOLDER / "data"
MODEL_FOLDER = DATA_FOLDER / 'models'


class DemoAnomalyDetector:

    def __init__(self) -> None:
        self._ml_model = None
        self._model_name = None
        os.makedirs(MODEL_FOLDER, exist_ok=True)
        CURRENT_MODEL_FOLDER = max(MODEL_FOLDER.glob("ae_model_*"), key=os.path.getctime, default=None)
        if CURRENT_MODEL_FOLDER and os.path.exists(CURRENT_MODEL_FOLDER):
            self._model_name = CURRENT_MODEL_FOLDER.absolute().name
            self._ml_model = core.AENetworkAnomaly.load(CURRENT_MODEL_FOLDER)

    def is_trained(self) -> bool:
        return self._ml_model is not None

    def get_model_name(self) -> str:
        return self._model_name
    
    def delete() -> None:
        if self._model_name and os.path.exists(self._model_name):
            os.remove(self._model_name)
            self._ml_model = None
            self._model_name = None

    def train(self, training_data: pd.DataFrame, labels: pd.DataFrame, force=False):
        if self._ml_model and not force:
            print(f"Model exists already. Model Name: {self._model_name}. Use force=True to retrain.")
            return
        
        self._ml_model = core.AENetworkAnomaly(n_inputs=training_data.shape[1]-1)

        # TODO Move this outside of this method
        # Get data up to current day (training set)
        # df_today = training_data.loc[training_data["timestamp"] < current_day.ctime()]

        # Remove from the training dataset those datapoints that are considered anomalous
        # This will allow the Autoencoder to only learn from the normal behaviour
        training_data = training_data[
            training_data['timestamp'].isin(labels[labels['label'] == 0]['timestamp'])]

        # Train the model
        clean_training_data = training_data.drop('timestamp',axis=1).values
        self._ml_model.fit(clean_training_data)
        self._model_name = f'ae_model_{time.time()}'
        print(f"Stored the model: {self._model_name}")

        # Store the trained model on the Model Registry
        self._ml_model.store(MODEL_FOLDER / self._model_name)
        
    def detect(self, prediction_data) -> dict:
        """
        Given the prediction data, this method returns the list of network anomalies detected and symptoms
        """
        if self._ml_model is None:
            raise Exception("The Anomaly Detector has not been trained yet.")

        X_pred = prediction_data.drop('timestamp',axis=1).values
        y_pred = self._ml_model.predict(X_pred, aggregate=False)
        model_predictions = self._ml_model.parse_predictions(prediction_data, y_pred)
        
        # Aggregate overlapping symptoms coming from different metrics
        day_symptoms = [
            (metric_id, symptom[0], symptom[1], symptom[2], symptom[3]) 
            for metric_id, symptoms_list in model_predictions.items() 
            for symptom in symptoms_list 
        ]
        # Sort by starting timestamp
        day_symptoms.sort(key=lambda x: x[1])

        # Create a list of incident in the form [(start_timestamp, end_timestamp, [symptom1, symptom2]),...]
        network_incidents = list()
        if len(day_symptoms) > 0:
            start = day_symptoms[0][1] 
            end = day_symptoms[0][2]
            network_incidents = [[start, end, [day_symptoms[0]]]]
            for symptom in day_symptoms[1:]:
                # if overlapping add to the current incident, new incident otherwise
                if symptom[1] <= end:
                    network_incidents[-1][2].append(symptom)
                    end = max(end, symptom[2])
                    network_incidents[-1][1] = end
                else:
                    start = symptom[1]
                    end = symptom[2]
                    network_incidents.append([start, end, [symptom]])
        return network_incidents
        
    def compare_models(self, other_model_name, eval_labels):
        from sklearn.metrics import classification_report
        other_model = core.AENetworkAnomaly.load(MODEL_FOLDER / other_model_name)
        current_model_prediction = self._ml_model.predict(eval_labels.drop('timestamp',axis=1).values, aggregate=False)
        print(classification_report(eval_labels, y_pred_champ, zero_division=1))
        return self._ml_model.compare(other_model)

    def _format_prediction_outut():
        """
        Aggregate overlapping symptoms coming from different metrics
        """

        day_symptoms = [
            (metric_id, symptom[0], symptom[1]) for metric_id, symptoms_list in model_predictions.items() for symptom in symptoms_list 
        ]

        # sort by starting timestamp
        day_symptoms.sort(key=lambda x: x[1])

        if len(day_symptoms) > 0:
            # create a list of incident in the form [(start_timestamp, end_timestamp, [symptom1, symptom2]),...]
            start = day_symptoms[0][1] 
            end = day_symptoms[0][2]
            network_incidents = [[start, end, [day_symptoms[0]]]]
            for symptom in day_symptoms[1:]:
                # if overlapping add to the current incident, new incident otherwise
                if symptom[1] <= end:
                    network_incidents[-1][2].append(symptom)
                    end = max(end, symptom[2])
                    network_incidents[-1][1] = end
                else:
                    start = symptom[1]
                    end = symptom[2]
                    network_incidents.append([start, end, [symptom]])
