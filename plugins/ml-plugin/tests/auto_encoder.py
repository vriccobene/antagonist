import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


class Vanilla_AE(nn.Module):
    """
    Feed-forward neural network with autoencoder architecture for anomaly detection using reconstruction error as an anomaly score.

    Parameters
    ----------
    n_inputs : int
        Number of input features.
    layer_sizes : list
        List containing the number of neurons in each layer of the encoder and decoder.
        The first element is the number of neurons in the first encoder layer,
        the second element is the number of neurons in the bottleneck layer (latent representation),
        and the third element is the number of neurons in the first decoder layer.

    Attributes
    ----------
    model : torch.nn.Module
        The autoencoder model.

    Examples
    -------
    >>> from Vanilla_AE import AutoEncoder
    >>> autoencoder = AutoEncoder(n_inputs=10, layer_sizes=[8, 4, 6])
    >>> autoencoder.fit(train_data)
    >>> predictions = autoencoder.predict(test_data)
    """

    def __init__(self, n_inputs: int, layer_sizes: list):
        super(Vanilla_AE, self).__init__()

        self.encoder = nn.Sequential(
            nn.Linear(n_inputs, layer_sizes[0]),
            nn.BatchNorm1d(layer_sizes[0]),
            nn.ReLU(),
            nn.Linear(layer_sizes[0], layer_sizes[1]),
            nn.BatchNorm1d(layer_sizes[1]),
            nn.ReLU(),
        )

        self.bottleneck = nn.Linear(layer_sizes[1], layer_sizes[2])

        # inverse sizes order of the encoder layers
        self.decoder = nn.Sequential(
            nn.Linear(layer_sizes[2], layer_sizes[1]),
            nn.BatchNorm1d(layer_sizes[1]),
            nn.ReLU(),
            nn.Linear(layer_sizes[1], layer_sizes[0]),
            nn.BatchNorm1d(layer_sizes[0]),
            nn.ReLU(),
            nn.Linear(layer_sizes[0], n_inputs),
        )

    def forward(self, x):
        encoded = self.encoder(x)
        bottleneck = self.bottleneck(encoded)
        decoded = self.decoder(bottleneck)
        return decoded

    def fit(
        self,
        data,
        early_stopping=True,
        validation_split=0.2,
        epochs=40,
        lr=0.001,
        batch_size=100,
        verbose=0,
        shuffle=True,
        patience=3,
        delta=0.001,
    ):
        """
        Train the autoencoder model on the provided data.

        Args:
            data (torch.Tensor): Input data for training.
            early_stopping (bool, optional): Whether to use early stopping during training. Defaults to True.
            validation_split (float, optional): Fraction of the training data to be used as validation data. Defaults to 0.2.
            epochs (int, optional): Number of training epochs. Defaults to 40.
            lr (float, optional): Learning rate for the optimizer. Defaults to 0.001.
            batch_size (int, optional): Batch size for training. Defaults to 100.
            verbose (int, optional): Verbosity mode (0 = silent, 1 = progress bar, 2 = current epoch and losses, 3 = each training iteration). Defaults to 0.
            shuffle (bool, optional): Whether to shuffle the training data before each epoch. Defaults to True.
            patience (int, optional): Number of epochs to wait before early stopping. Defaults to 5.
            delta (float, optional): Minimum change in the monitored quantity to qualify as an improvement. Defaults to 0.001.
        """

        self.shape = data.shape[1]
        criterion = nn.L1Loss()
        optimizer = optim.Adam(self.parameters(), lr=lr)

        # Split data into train and validation
        num_val = int(validation_split * data.shape[0])
        num_train = data.shape[0] - num_val
        data=torch.Tensor(data)
        train_data, val_data = torch.utils.data.random_split(data, [num_train, num_val])

        train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=shuffle)
        val_loader = DataLoader(val_data, batch_size=batch_size, shuffle=False)

        best_loss = float("inf")
        early_stop_counter = 0

        for epoch in range(epochs):
            train_loss = 0.0
            for inputs in train_loader:
                optimizer.zero_grad()
                outputs = self(inputs)
                loss = criterion(outputs, inputs)
                loss.backward()
                optimizer.step()
                train_loss += loss.item() * inputs.size(0)

            if verbose > 0:
                print(
                    f"Epoch: {epoch+1}, Train Loss: {train_loss/len(train_loader.dataset)}"
                )

            if early_stopping:
                val_loss = 0.0
                with torch.no_grad():
                    for inputs in val_loader:
                        outputs = self(inputs)
                        loss = criterion(outputs, inputs)
                        val_loss += loss.item() * inputs.size(0)
                val_loss /= len(val_loader.dataset)

                if val_loss < best_loss - delta:
                    best_loss = val_loss
                    early_stop_counter = 0
                else:
                    early_stop_counter += 1
                    if early_stop_counter >= patience:
                        print(f"Early stopping at epoch {epoch+1}")
                        break

    def predict(self, data):
        """
        Generate predictions using the trained autoencoder model.

        Parameters
        ----------
        data : torch.Tensor
            Input data for making predictions.

        Returns
        -------
        torch.Tensor
            The reconstructed output predictions.
        """

        data=torch.Tensor(data)
        self.eval()
        with torch.no_grad():
            outputs = self(data)
        return outputs.numpy()
