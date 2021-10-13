

class BaseModel():

    def __init__(self, **kwargs):
        pass

    def fit(self, dataset):
        """
        inputs:
            dataset - a dataset containing data

        outputs:
            model - a trained model
        """
        raise(NotImplementedError)

    def predict(self, X):
        """
        Predict for one recording

        inputs:
            X - a single recording torch.tensor (T by C by feature dim)

        outputs:
            y_hat - maximum class label length T torch.tensor
        """
        raise(NotImplementedError)
