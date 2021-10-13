import sklearn.ensemble
import sklearn.linear_model
from sklearn.svm import SVC, LinearSVC
import numpy as np

from models.basemodel import BaseModel


class SklearnMixin():
    """A mixin for wrapping sklearn classifiers

    Implements fit, predict_proba, and predict for sklearn classifiers
    """

    def fit(self, dataset):
        X = dataset.get_all_data()
        X = X.numpy()
        X = X.reshape(X.shape[0], -1)
        y = dataset.get_all_labels().numpy()
        self.model = self.model.fit(X, y)

    def predict_proba(self, X):
        X = X.to('cpu').numpy()
        X = X.reshape(X.shape[0], -1)
        pred = self.model.predict_proba(X)
        return pred

    def predict(self, X):
        X = X.to('cpu').numpy()
        X = X.reshape(X.shape[0], -1)
        pred = self.model.predict(X)
        return pred


class LogisticRegression(SklearnMixin, BaseModel):

    def __init__(self, **kwargs):
        self.model = (
            sklearn.linear_model.LogisticRegression(**kwargs)
        )


class RandomForest(SklearnMixin, BaseModel):

    def __init__(self, **kwargs):
        self.model = (
            sklearn.ensemble.RandomForestClassifier(**kwargs)
        )


class SupportVectorMachine(SklearnMixin, BaseModel):
    def __init__(self, **kwargs):
        self.model = SVC(**kwargs)

    def predict_proba(self, X):
        """SVM has no predict_proba"""
        X = X.to('cpu').numpy()
        X = X.reshape(X.shape[0], -1)
        pred = self.model.predict(X)
        pred_reshape = np.zeros((X.shape[0], 2))
        pred_reshape[:, 0] = 1 - pred
        pred_reshape[:, 1] = pred
        return pred_reshape


class LinearSupportVectorMachine(SklearnMixin, BaseModel):
    def __init__(self, **kwargs):
        self.model = LinearSVC(**kwargs)

    def predict_proba(self, X):
        """SVM has no predict_proba"""
        X = X.to('cpu').numpy()
        X = X.reshape(X.shape[0], -1)
        pred = self.model.predict(X)
        pred_reshape = np.zeros((X.shape[0], 2))
        pred_reshape[:, 0] = 1 - pred
        pred_reshape[:, 1] = pred
        return pred_reshape
