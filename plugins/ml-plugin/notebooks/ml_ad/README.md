## Machine Learning Anomaly Detection package

Folder structure

```
- ml_ad_
    |- auto_encoder.py
    |- core.py
    |- utils.py
    |- __init__.py
```

### auto_encoder.py

Contains the PyTorch code implementing a Feed-forward neural network with autoencoder architecture for anomaly detection using reconstruction error as an anomaly score.

The `Vanilla_AE` class contains the prediction and the training code.


### core.py

Code defining a class called AENetworkAnomaly which is used for detecting anomalies in time series data using an Autoencoder Neural Network.

The class is designed to handle the end-to-end process of training an autoencoder model for anomaly detection in time series data. It provides methods for fitting the model, making predictions, parsing the predictions into interpretable intervals, and saving/loading the trained model and associated artifacts.

Attributes:

- `n_inputs`: The number of input metrics in the time series data.
- `layer_sizes`: A list of integers representing the sizes of the hidden layers in the autoencoder.
- `lr`, `batch_size`, `epochs`, `validation_split`, `early_stopping`, `patience`, `Q`: Hyperparameters for training the autoencoder model.
- `ae`: The trained autoencoder model (instance of Vanilla_AE class).
- `scaler`: The scaler used to normalize the input data.
- `threshold`: The anomaly threshold for each input metric.

Methods:

- `fit(X)`: Trains the autoencoder model on the input data X.
- `is_trained()`: Checks if the autoencoder model has been trained.
- `predict(X, aggregate=False)`: Predicts anomalies in the input data X. If aggregate=True, it returns a single boolean value indicating whether any anomaly is present; otherwise, it returns a boolean array indicating anomalies for each input metric (symptoms).
- `parse_predictions(df_data, predictions)`: Parses the anomaly predictions into intervals (start, end timestamps) for each input metric.
- `store(model_folder)`: Stores the trained model, scaler, threshold, and parameters in the specified folder.
- `load(model_folder)`: Loads a previously trained model from the specified folder.

