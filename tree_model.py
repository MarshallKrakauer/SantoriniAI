import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.model_selection import train_test_split

import game

GBM_MODEL = joblib.load('gbm_classifier.joblib')


def get_predictions(model, X_train_orig, y_train_orig, X_test_orig):
    """
    Obtain probability and class predictions for a given dataset and model

    Parameters
    ----------
    model : object with a fit, predict, and predict_proba method function
        Machine learning model from which to produce predictions
    X_test_orig : pandas DataFrame
        Dataframe with features from which to produce a prediction
    y_train_orig : list or pandas series
        Target variables to train model on
    X_train_orig : pandas DataFrame
        Testing values from which to validate model

    Returns
    -------
    Tuple
        Two lists: the class (1 or 0) predictions and the probability predictions
    """
    model.fit(X_train_orig, y_train_orig)
    y_pred_class = model.predict(X_test_orig)
    y_pred_prob = model.predict_proba(X_test_orig)
    y_pred_prob = [elem[1] for elem in y_pred_prob]

    return y_pred_class, y_pred_prob


def analyze_accuracy(y_test_acc, y_pred_prob_acc, y_pred_class_acc):
    """
    Show AUC curve and confusion matrix for model predictions

    Parameters
    ----------
    y_test_acc : list or pandas series
        True values that are attempting to be predicted

    y_pred_class_acc : list
        Probability predictions for each row

    y_pred_prob_acc : list
        Class predictions (1 or 0) for each row


    """
    naive_prediction = [0.5] * len(y_pred_class_acc)

    naive_auc = roc_auc_score(y_test_acc, naive_prediction)
    md_auc = roc_auc_score(y_test_acc, y_pred_prob_acc)
    print('No Skill: ROC AUC=%.3f' % naive_auc)
    print('Model   : ROC AUC=%.3f' % md_auc)

    ns_fpr, ns_tpr, _ = roc_curve(y_test_acc, naive_prediction)
    lr_fpr, lr_tpr, _ = roc_curve(y_test_acc, y_pred_prob_acc)


if __name__ == '__main__':
    # Setup Data for Prediction Modeling
    df = pd.read_csv('game_list.csv')
    df = df.loc[df.iloc[:, 1] <= (20 / 60), :]
    y = df.iloc[:, 0]
    X = df.iloc[:, 1:]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Set up GBM Model
    gbm = GradientBoostingClassifier(loss='deviance', random_state=0, n_estimators=100,
                                     max_depth=3, subsample=1, min_impurity_decrease=0)

    gbm_sigmoid = CalibratedClassifierCV(gbm, method='sigmoid', cv=3)
    gbm_sigmoid.fit(X_train, y_train)
    y_class, y_prob = get_predictions(gbm_sigmoid, X_train, y_train, X_test)
    gbm.fit(X_train, y_train)

    joblib.dump(gbm, 'gbm_classifier.joblib')
    clf = joblib.load('gbm_classifier.joblib')

    # <editor-fold desc="Create Test Game">
    test_game = game.Game()
    test_game.board[1][1]['occupant'] = 'W'
    test_game.board[2][1]['occupant'] = 'W'

    test_game.board[3][1]['occupant'] = 'G'
    test_game.board[3][3]['occupant'] = 'G'

    test_game.board[1][2]['level'] = 2
    test_game.board[0][2]['level'] = 1
    test_game.board[4][3]['level'] = 1
    test_game.board[4][4]['level'] = 1
    test_game.board[4][0]['level'] = 3

    test_game.board[2][2]['occupant'] = 'X'
    test_game.board[2][2]['level'] = 4
    # </editor-fold>
