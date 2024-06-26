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
    """
    A class for detecting anomalies in time series data using an Autoencoder Neural Network.

    Attributes:
        n_inputs (int): The number of input features.
        layer_sizes (List[int]): A list of integers representing the sizes of the hidden layers in the autoencoder.
        lr (float): The learning rate for training the autoencoder.
        batch_size (int): The batch size for training the autoencoder.
        epochs (int): The number of epochs for training the autoencoder.
        validation_split (float): The fraction of the training data to be used for validation.
        early_stopping (bool): Whether to use early stopping during training.
        patience (int): The number of epochs to wait before early stopping when the validation loss stops improving.
        Q (float): The quantile value used to calculate the anomaly threshold.
        ae (Vanilla_AE): The trained autoencoder model.
        scaler (StandardScaler): The scaler used to normalize the input data.
        threshold (pd.Series): The anomaly threshold for each input feature.

    Methods:
        fit(X): Trains the autoencoder model on the input data X.
        is_trained(): Checks if the autoencoder model has been trained.
        predict(X, aggregate=False): Predicts anomalies in the input data X.
        parse_predictions(df_data, predictions): Parses the anomaly predictions into intervals for each input feature.
        store(model_folder): Stores the trained model, scaler, threshold, and parameters in the specified folder.
        load(model_folder): Loads a previously trained model from the specified folder.
    """

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
        """
        Trains the autoencoder model on the input data X.

        Args:
            X (pd.DataFrame): The input data for training.
        """

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
        """
        Checks if the autoencoder model has been trained.

        Returns:
            bool: True if the model has been trained, False otherwise.
        """
        return self.ae is not None

    def predict(self, X, aggregate=False):
        """
        Predicts anomalies in the input data X.

        Args:
            X (pd.DataFrame): The input data for prediction.
            aggregate (bool): If True, returns a single boolean value indicating whether any anomaly is present.
                              If False, returns a boolean array indicating anomalies for each input sample.

        Returns:
            np.ndarray or bool: A boolean array or a single boolean value indicating anomalies.
        """

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
        """
        Parses the anomaly predictions into intervals for each input feature.

        Args:
            df_data (pd.DataFrame): The input data used for prediction.
            predictions (np.ndarray): The boolean array of anomaly predictions.

        Returns:
            dict: A dictionary mapping feature indices to a list of anomaly intervals (start, end) timestamps.
        """
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
        """
        Stores the trained model, scaler, threshold, and parameters in the specified folder.

        Args:
            model_folder (str): The path to the folder where the model and related files will be stored.
        """
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
        """
        Loads a previously trained model from the specified folder.

        Args:
            model_folder (str): The path to the folder containing the model and related files.

        Returns:
            AENetworkAnomaly: The loaded AENetworkAnomaly instance.
        """
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
