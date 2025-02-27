import random
from functools import partial

import numpy as np
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from imodels import HSTreeClassifier, HSTreeClassifierCV, \
    HSTreeRegressor, HSTreeRegressorCV


class TestShrinkage:
    '''Tests simple classification for different models. Note: still doesn't test all the models!
    '''

    def setup(self):
        np.random.seed(13)
        random.seed(13)
        self.n = 20
        self.p = 2
        self.X_classification_binary = (np.random.randn(self.n, self.p) > 0).astype(int)

        # y = x0 > 0
        self.y_classification_binary = (self.X_classification_binary[:, 0] > 0).astype(int)

        # flip labels for last few
        self.y_classification_binary[-2:] = 1 - self.y_classification_binary[-2:]
        self.X_regression = np.random.randn(self.n, self.p)
        self.y_regression = self.X_regression[:, 0] + np.random.randn(self.n) * 0.01

    def test_classification_shrinkage(self):
        '''Test imodels on basic binary classification task
        '''
        for model_type in [
            partial(HSTreeClassifier, estimator_=DecisionTreeClassifier()),
            partial(HSTreeClassifierCV, estimator_=DecisionTreeClassifier()),
            # partial(HSC45TreeClassifierCV, estimator_=C45TreeClassifier()),
            # partial(HSOptimalTreeClassifierCV, estimator_=OptimalTreeClassifier()),
        ]:
            init_kwargs = {}
            m = model_type(**init_kwargs)

            X = self.X_classification_binary
            m.fit(X, self.y_classification_binary)

            # test predict()
            preds = m.predict(X)  # > 0.5).astype(int)
            assert preds.size == self.n, 'predict() yields right size'

            # test preds_proba()
            preds_proba = m.predict_proba(X)
            assert len(preds_proba.shape) == 2, 'preds_proba has 2 columns'
            assert preds_proba.shape[1] == 2, 'preds_proba has 2 columns'
            assert np.max(preds_proba) < 1.1, 'preds_proba has no values over 1'
            assert (np.argmax(preds_proba, axis=1) == preds).all(), ("predict_proba and ""predict correspond")

            # test acc
            acc_train = np.mean(preds == self.y_classification_binary)
            # print(type(m), m, 'final acc', acc_train)
            assert acc_train > 0.8, 'acc greater than 0.8'

    def test_regression_shrinkage(self):
        '''Test imodels on basic binary classification task
        '''
        for model_type in [partial(HSTreeRegressor, estimator_=DecisionTreeRegressor()),
                           partial(HSTreeRegressorCV, estimator_=DecisionTreeRegressor()),
                           ]:
            m = model_type()
            m.fit(self.X_regression, self.y_regression)

            preds = m.predict(self.X_regression)
            assert preds.size == self.n, 'predictions are right size'

            mse = np.mean(np.square(preds - self.y_regression))
            assert mse < 1, 'mse less than 1'


if __name__ == '__main__':
    t = TestShrinkage()
    t.setup()
    t.test_classification_shrinkage()
