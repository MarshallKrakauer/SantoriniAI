import time

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.model_selection import train_test_split

import game

GBM_MODEL = joblib.load('gbm_classifier.joblib')


def get_predictions(model, X_train_orig, y_train_orig, X_test_orig):
    model.fit(X_train_orig, y_train_orig)
    y_pred_class = model.predict(X_test_orig)
    y_pred_prob = model.predict_proba(X_test_orig)
    y_pred_prob = [elem[1] for elem in y_pred_prob]

    return y_pred_class, y_pred_prob


def analyze_accuracy(y_test_acc, y_pred_prob_acc, y_pred_class_acc):
    naive_prediction = [0.5] * len(y_pred_class_acc)

    naive_auc = roc_auc_score(y_test_acc, naive_prediction)
    md_auc = roc_auc_score(y_test_acc, y_pred_prob_acc)
    print('No Skill: ROC AUC=%.3f' % naive_auc)
    print('Model   : ROC AUC=%.3f' % md_auc)

    ns_fpr, ns_tpr, _ = roc_curve(y_test_acc, naive_prediction)
    lr_fpr, lr_tpr, _ = roc_curve(y_test_acc, y_pred_prob_acc)


def plot_calibration(y_test_calibration, y_prob_calibration):
    fop, mpv = calibration_curve(y_test_calibration, y_prob_calibration, n_bins=10, normalize=True)
    # plot perfectly calibrated
    plt.plot([0, 1], [0, 1], linestyle='--')
    # plot model reliability
    plt.plot(mpv, fop, marker='.')
    plt.show()


if __name__ == '__main__':

    # Setup Data for Prediction Modeling
    df = pd.read_csv('game_list.csv')
    df = df.loc[df.iloc[:, 1] <= (20/60), :]
    print(df.shape)
    y = df.iloc[:, 0]
    X = df.iloc[:, 1:]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Set up GBM Model
    gbm = GradientBoostingClassifier(loss='deviance', random_state=0, n_estimators=100,
                                     max_depth=3, subsample=1, min_impurity_decrease=0)

    # Aside, build XGBoost model. Poorly calibrated, so it's not used
    params = {'booster': 'gbtree', 'eval_metric': 'logloss', 'max_depth': 3,
              'gamma': 0.1, 'colsample_bytree': 1, 'subsample': 1, 'min_child_weight': 3, 'n_jobs': -1,
              'objective': 'binary:logistic'}
    xgb_matrix = xgb.DMatrix(X_train, label=y_train)
    gbm.fit(X_train, y_train)
    booster = xgb.train(params=params, dtrain=xgb_matrix, num_boost_round=100)
    # </editor-fold>

    gbm_sigmoid = CalibratedClassifierCV(gbm, method='sigmoid', cv=3)
    gbm_sigmoid.fit(X_train, y_train)
    y_class, y_prob = get_predictions(gbm_sigmoid, X_train, y_train, X_test)

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