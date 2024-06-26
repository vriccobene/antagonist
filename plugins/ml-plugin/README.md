## Antagonist ML Plugin

Folder structure

```
- ml-plugin
    |- antagonist_ml
    |---- service.py
    |- notebooks
    |---- ml_ad [python pkg]
    |---- utils [python pkg]
    |---- detection_stage.ipynb
    |---- retaining_stage.ipynb
    |- requirements.txt
```

The `ml-plugin` is composed of two folders: `antagonist_ml` contains the set of functions in charge of reading and writing the network anomaly labels from/into antagonist; the `notebooks` folder containins the Jupyther notebooks simulating the processes to apply and re-train network anomaly detection systems (in this case, a deep auto-encoder).  

This code structure is based on the following assumption:
Antagonist is only responsible for providing label management functionalities in the context of anomaly detection. The machine learning routines (prediciton, training, re-training, and deploy) are delegated to completely external components. This because every operator can have its own ML platform and models (e.g., Tensorflow, PyTorch, Flink, etc.).

### antagonist-ml

This service needs to provide the following functionalities:
- Read the network anomaly / symptom labels related to a particular service/subservice.
- Write the network anomaly / symptom labels related to a particular service/subservice.

More details are available in the methods documentations.

### notebooks

#### ml_ad

Python package containing the torch code to train, store and load a naive Auto-Encoder model based on the PyTorch framework. More informations are available in the `ml_ad` folder.

#### utils

Python package containing the python code to read the data from either InfluxDB or the dataset folder. Currently, it also reads the labels from the dataset folder.

#### detection_stage.ipynb

Jupyter notebook providing the code to:

1. Read the dataset from its folder (to be substituted by the read function from InfluxDB and Antagonist) up to a certain date (`current_day`).
2. Split the dataset in train and prediciton set 
    - data before current date with labels to train the model on
    - current day data (00:00-23:59) where to apply the model on
3. Load the model trained on the train data if present, otherwise, train it on the fly
4. Predict the labels for the current day data
5. Store prediction in Antagonist using functions from `antagonist_ml`.

#### retaining_stage.ipynb

Jupyter notebook providing the code to:

1. Read the dataset from its folder (to be substituted by the read function from InfluxDB and Antagonist) up to a certain date (`current_day`).
2. Split the dataset in train and prediciton set 
    - data before current date with labels to train the model on
    - current day data (00:00-23:59) where to evaluate the model on
3. Train the new model on the train data
4. Load the current deploy model to compare with (`champion_model`)
5. Predict the labels for the current day data with both the models
6. Compare the performance using sklearn classification report (point-wise metrics)