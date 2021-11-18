import numpy as np
import sklearn.ensemble
import sklearn.linear_model
import matplotlib.pyplot as plt

from models.basemodel import BaseModel


class SklearnChannelMixin():
    """A mixin for wrapping sklearn classifiers for channel based classification

    Implements fit, predict_proba, and predict for sklearn channel classifiers
    """

    def fit(self, dataset):
        # Reshape as (TxC, F)
        X = dataset.get_all_data().numpy()
        T, C, F = X.shape
        X = X.reshape(-1, F)
        # Repeat labels C times
        y = dataset.get_all_labels().numpy()
        y = np.repeat(y, C)
        self.model = self.model.fit(X, y)

    def predict_proba(self, X):
        T, C, F = X.shape
        X = X.to('cpu').numpy()
        # Reshape as (TxC, F)
        X = X.reshape(T*C, F)
        # Predict and reshape
        pred = self.model.predict_proba(X)
        pred = pred.reshape(T, C, 2)
        maxes = np.amax(pred[:, :, 1], axis=1)
        mins = np.min(pred[:, :, 0], axis=1)
        pred = np.zeros((T, 2))
        pred[:, 1] = maxes
        pred[:, 0] = mins
        return pred

    def predict(self, X):
        T, C, F = X.shape
        X = X.to('cpu').numpy()
        # Reshape as (TxC, F)
        X = X.reshape(T*C, F)
        # Predict and reshape
        pred = self.model.predict(X)
        pred = pred.reshape(T, C, 2)
        maxes = np.amax(pred[:, :, 1], axis=1)
        mins = np.min(pred[:, :, 0], axis=1)
        pred = np.zeros((T, 2))
        pred[:, 1] = maxes
        pred[:, 0] = mins
        return pred

    def predict_channel(self, X):
        """Predict the channel based classifications
        """
        X = X.to('cpu').numpy()
        T, C, F = X.shape
        # Reshape as (TxC, F)
        X = X.reshape(-1, X.shape[2])
        # Predict and reshape
        pred = self.model.predict(X)
        pred = pred.reshape(T, C, 2)
        return pred

    def predict_channel_proba(self, X):
        """Predict the channel based classifications
        """
        X = X.to('cpu').numpy()
        T, C, F = X.shape
        # Reshape as (TxC, F)
        X = X.reshape(-1, X.shape[2])
        # Predict and reshape
        pred = self.model.predict_proba(X)
        pred = pred.reshape(T, C, 2)
        return pred


class LogisticRegressionChannel(SklearnChannelMixin, BaseModel):

    def __init__(self, **kwargs):
        self.model = (
            sklearn.linear_model.LogisticRegression(**kwargs)
        )


class RandomForestChannel(SklearnChannelMixin, BaseModel):

    def __init__(self, **kwargs):
        self.model = (
            sklearn.ensemble.RandomForestClassifier(**kwargs)
        )
