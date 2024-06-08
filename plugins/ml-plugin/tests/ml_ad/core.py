import os
import torch
import pickle
import logging
import pandas as pd

from typing import List
from collections import defaultdict
from sklearn.preprocessing import StandardScaler

from .auto_encoder import Vanilla_AE
from .utils import find_consecutive_true_np

logger = logging.getLogger(__name__)
# configure logger to print date
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class AENetworkAnomaly:

    def __init__(
        self,
        n_inputs: int,
        layer_sizes: List[int] = [8, 4, 2],
        lr: float = 0.005,
        batch_size: int = 32,
        epochs: int = 40,
        validation_split: float = 0.2,
        early_stopping: bool = True,
        patience: int = 3,
        Q: float = 0.99,
        **kwargs,
    ):
        self.n_inputs = n_inputs
        self.layer_sizes = layer_sizes
        self.lr = lr
        self.batch_size = batch_size
        self.epochs = epochs
        self.validation_split = validation_split
        self.early_stopping = early_stopping
        self.patience = patience
        self.Q = Q

        self.ae = None
        self.scaler = None
        self.threshold = None

    def fit(self, X):

        self.ae = Vanilla_AE(n_inputs=self.n_inputs, layer_sizes=self.layer_sizes)

        # scaler init and fitting
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # model fitting
        self.ae.fit(
            X_scaled,
            early_stopping=self.early_stopping,
            validation_split=self.validation_split,
            epochs=self.epochs,
            lr=self.lr,
            batch_size=self.batch_size,
            verbose=0,
            shuffle=True,
            patience=self.patience,
            delta=0.001,
        )

        # results predicting
        residuals_train = pd.DataFrame(X_scaled - self.ae.predict(X_scaled)).abs()
        self.threshold = residuals_train.quantile(self.Q, axis=0) * 5 / 2

    def is_trained(self):
        return self.ae is not None

    def predict(self, X, aggregate=False):

        if self.is_trained():
            X_hat = self.scaler.transform(X)
            residuals_full_df = X_hat - self.ae.predict(X_hat)
            residuals_full_df = pd.DataFrame(residuals_full_df).abs()

            symptoms = (residuals_full_df > self.threshold).values

            return symptoms.any(axis=1) if aggregate else symptoms
        else:
            logger.warning("Model not trained yet.")
            return None

    def parse_predictions(self, df_data, predictions):
        intervals = find_consecutive_true_np(predictions)
        symptoms_per_metric = defaultdict(list)

        for metric_id, symptoms in enumerate(intervals):
            for symp in symptoms:
                symptoms_per_metric[metric_id].append(
                    [
                        df_data["timestamp"].iloc[symp[0]].timestamp(),
                        df_data["timestamp"].iloc[symp[1] - 1].timestamp(),
                    ]
                )

        return symptoms_per_metric

    def store(self, model_folder):
        """Stores the torch model, the scaler, the parameters and the threshold into the input folder."""
        if self.is_trained():
            os.makedirs(model_folder, exist_ok=True)
            torch.save(self.ae.state_dict(), os.path.join(model_folder, "ae_model.pt"))
            with open(os.path.join(model_folder, "scaler.pkl"), "wb") as f:
                pickle.dump(self.scaler, f)
            with open(os.path.join(model_folder, "threshold.pkl"), "wb") as f:
                pickle.dump(self.threshold, f)
            with open(os.path.join(model_folder, "params.pkl"), "wb") as f:
                pickle.dump(self.__dict__, f)
        else:
            logger.warning("Model not trained yet.")

    @staticmethod
    def load(model_folder):
        """Loads the torch model, the scaler, the parameters and the threshold from the input folder."""
        ae_state = torch.load(os.path.join(model_folder, "ae_model.pt"))
        with open(os.path.join(model_folder, "scaler.pkl"), "rb") as f:
            scaler = pickle.load(f)
        with open(os.path.join(model_folder, "threshold.pkl"), "rb") as f:
            threshold = pickle.load(f)
        with open(os.path.join(model_folder, "params.pkl"), "rb") as f:
            params = pickle.load(f)

        model = AENetworkAnomaly(**params)
        model.ae = Vanilla_AE(n_inputs=params["n_inputs"], layer_sizes=params["layer_sizes"])
        model.ae.load_state_dict(ae_state)
        model.scaler = scaler
        model.threshold = threshold

        return model
