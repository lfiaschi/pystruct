import numpy as np

from pyqpbo import binary_grid
from pyqpbo import alpha_expansion_grid


class StructuredProblem(object):
    def __init__(self):
        self.size_psi = None

    def psi(self, x, y):
        pass

    def inference(self, x, w):
        pass

    def loss(self, y, y_hat):
        pass


class BinaryGridCRF(StructuredProblem):
    def __init__(self):
        self.n_labels = 2
        # three parameter for binary, one for unaries
        self.size_psi = 4

    def psi(self, x, y):
        # x is unaries
        # y is a labeling
        ## unary features:
        gx, gy = np.ogrid[:x.shape[0], :x.shape[1]]
        unaries_acc = np.sum(x[gx, gy, y])

        ##accumulated pairwise
        #make one hot encoding
        labels = np.zeros((y.shape[0], y.shape[1], self.n_labels),
                dtype=np.int)
        gx, gy = np.ogrid[:y.shape[0], :y.shape[1]]
        labels[gx, gy, y] = 1
        # vertical edges
        vert = np.dot(labels[1:, :, :].reshape(-1, 2).T, labels[:-1, :,
           :].reshape(-1, 2))
        # horizontal edges
        horz = np.dot(labels[:, 1:, :].reshape(-1, 2).T, labels[:, :-1,
           :].reshape(-1, 2))
        pw = vert + horz
        pw[0, 1] += pw[1, 0]
        #pw = np.zeros((2, 2))
        return np.array([unaries_acc, pw[0, 0], pw[0, 1], pw[1, 1]])

    def loss(self, y, y_hat):
        # hamming loss:
        return np.sum(y != y_hat)

    def inference(self, x, w):
        unary_param = w[0]
        pairwise_params = np.array([[w[1], w[2]], [w[2], w[3]]])
        unaries = - 10 * unary_param * x
        pairwise = -10 * pairwise_params
        y = binary_grid(unaries.astype(np.int32), pairwise.astype(np.int32))
        return y


class MultinomialGridCRF(StructuredProblem):
    def __init__(self, n_labels):
        self.n_labels = n_labels
        # n_labels unary parameters, upper triangular for pairwise
        self.size_psi = n_labels + n_labels * (n_labels + 1) / 2

    def psi(self, x, y):
        # x is unaries
        # y is a labeling
        ## unary features:
        gx, gy = np.ogrid[:x.shape[0], :x.shape[1]]
        selected_unaries = x[gx, gy, y]
        unaries_acc = np.sum(x[gx, gy, y])
        unaries_acc = np.bincount(y.ravel(), selected_unaries.ravel(),
                minlength=self.n_labels)

        ##accumulated pairwise
        #make one hot encoding
        labels = np.zeros((y.shape[0], y.shape[1], self.n_labels),
                dtype=np.int)
        gx, gy = np.ogrid[:y.shape[0], :y.shape[1]]
        labels[gx, gy, y] = 1
        # vertical edges
        vert = np.dot(labels[1:, :, :].reshape(-1, self.n_labels).T,
                labels[:-1, :, :].reshape(-1, self.n_labels))
        # horizontal edges
        horz = np.dot(labels[:, 1:, :].reshape(-1, self.n_labels).T, labels[:,
            :-1, :].reshape(-1, self.n_labels))
        pw = vert + horz
        pw = pw + pw.T - np.diag(np.diag(pw))
        feature = np.hstack([unaries_acc, pw[np.tri(self.n_labels,
            dtype=np.bool)]])
        return feature

    def loss(self, y, y_hat):
        # hamming loss:
        return np.sum(y != y_hat)

    def inference(self, x, w):
        unary_params = w[:self.n_labels]
        pairwise_flat = np.asarray(w[self.n_labels:])
        pairwise_params = np.zeros((self.n_labels, self.n_labels))
        pairwise_params[np.tri(self.n_labels, dtype=np.bool)] = pairwise_flat
        pairwise_params = pairwise_params + pairwise_params.T\
                - np.diag(np.diag(pairwise_params))
        unaries = (- 10 * unary_params * x).astype(np.int32)
        pairwise = (-10 * pairwise_params).astype(np.int32)
        y = alpha_expansion_grid(unaries, pairwise)
        return y