# check pytorch version
# Based on this: https://machinelearningmastery.com/pytorch-tutorial-develop-deep-learning-models/
from sklearn.metrics import accuracy_score
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from torch import Tensor
from torch.nn import Linear
from torch.nn import ReLU
from torch.nn import Sigmoid
from torch.nn import Module
from torch.optim import SGD, Adam
from torch.nn import BCELoss
from torch.nn.init import kaiming_uniform_
from torch.nn.init import xavier_uniform_
import pandas as pd
import numpy as np


class NNDataset(Dataset):
    # load the dataset
    def __init__(self):
        # load the csv file as a dataframe
        df = pd.read_csv('game_list.csv', header=None)
        # df = df.loc[df.iloc[:, 1] * 60 <= 12, :]
        # store the inputs and outputs
        self.features = df.values[:, 1:]
        self.target = df.values[:, 0]
        # ensure input data is floats
        self.features = self.features.astype('float32')
        # label encode target and ensure the values are floats
        self.target = self.target.astype('float32')
        self.target = self.target.reshape((len(self.target), 1))

    # number of rows in the dataset
    def __len__(self):
        return len(self.features)

    # get a row at an index
    def __getitem__(self, idx):
        return [self.features[idx], self.target[idx]]

    # get indexes for train and test rows
    def get_splits(self, test_proportion=0.2):
        # determine sizes
        test_size = round(test_proportion * len(self.features))
        train_size = len(self.features) - test_size
        # calculate the split
        return random_split(self, [train_size, test_size])


class NeuralNetwork(Module):
    # define model elements
    def __init__(self, n_inputs):
        super(NeuralNetwork, self).__init__()
        # input to first hidden layer
        self.hidden1 = Linear(n_inputs, 100)
        kaiming_uniform_(self.hidden1.weight, nonlinearity='relu')
        self.act1 = ReLU()
        # second hidden layer
        self.hidden2 = Linear(100, 50)
        kaiming_uniform_(self.hidden2.weight, nonlinearity='relu')
        self.act2 = ReLU()
        # third hidden layer and output
        self.hidden3 = Linear(50, 1)
        xavier_uniform_(self.hidden3.weight)
        self.act3 = Sigmoid()

    # forward propagate input
    def forward(self, santorini_board_features):
        # input to first hidden layer
        santorini_board_features = self.hidden1(santorini_board_features)
        santorini_board_features = self.act1(santorini_board_features)
        # second hidden layer
        santorini_board_features = self.hidden2(santorini_board_features)
        santorini_board_features = self.act2(santorini_board_features)
        # third hidden layer and output
        santorini_board_features = self.hidden3(santorini_board_features)
        santorini_board_features = self.act3(santorini_board_features)

        return santorini_board_features


# prepare the dataset
def prepare_data():
    # load the dataset
    dataset = NNDataset()
    # calculate split
    train, test = dataset.get_splits()
    # prepare data loaders
    train_dl = DataLoader(train, batch_size=32, shuffle=True)
    test_dl = DataLoader(test, batch_size=32, shuffle=False)
    return train_dl, test_dl


# train the model
def train_nn_model(train_dl, model):
    # define the optimization
    criterion = BCELoss()  # binary cross entropy
    #optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9)
    optimizer = Adam(params=model.parameters(), lr=0.001)
    # enumerate epochs
    for epoch in range(100):
        # enumerate mini batches
        for i, (inputs, targets) in enumerate(train_dl):
            # clear the gradients
            optimizer.zero_grad()
            # compute the model output
            y_hat = model(inputs)
            # calculate loss
            loss = criterion(y_hat, targets)
            # credit assignment
            loss.backward()
            # update model weights
            optimizer.step()

    return optimizer


def evaluate_model(test_dl, model):
    predictions, actuals, probs = list(), list(), list()
    for i, (inputs, targets) in enumerate(test_dl):
        # evaluate the model on the test set
        yhat = model(inputs)
        # retrieve numpy array
        yhat = yhat.detach().numpy()
        actual = targets.numpy()
        actual = actual.reshape((len(actual), 1))
        probs.append([np.round(yhat.astype(float)[0][0],2), actual.astype(float)[0][0]])
        # round to class values
        yhat = yhat.round()
        # store
        predictions.append(yhat)
        actuals.append(actual)
    predictions, actuals = np.vstack(predictions), np.vstack(actuals)
    # calculate accuracy
    acc = accuracy_score(actuals, predictions)
    return acc, probs

def get_values():
    pass

# make a class prediction for one row of data
def predict(row, model):
    # convert row to data
    row = Tensor([row])
    # make prediction
    y_hat = model(row)
    # retrieve numpy array
    y_hat = y_hat.detach().numpy()
    return y_hat

# Initial Neural Network RUn
model = NeuralNetwork(186)
train_dl, test_dl = prepare_data()
train_nn_model(train_dl, model)

acc, predictions = evaluate_model(test_dl, model)
print(predictions)