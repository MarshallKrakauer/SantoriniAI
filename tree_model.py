from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import pandas as pd
import joblib
import game
from data_creation import SantoriniData

XGB_MODEL = clf = joblib.load('xgb_classifier.joblib')

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
    rf = RandomForestClassifier(n_estimators=100, random_state=0)
    xgb = XGBClassifier(booster='gbtree', random_state=0, use_label_encoder=False,
                        eval_metric='logloss', n_estimators=200, max_depth=3, gamma=0.1, colsample_bytree=1,
                        subsample=1, min_child_weight=3, n_jobs=-1)
    params = {'booster' }

    df = pd.read_csv('game_list.csv', header=None)
    y = df.iloc[:, 0]
    X = df.iloc[:, 1:]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    xgb.fit(X_train, y_train)
    xgb_sigmoid = CalibratedClassifierCV(xgb, method='sigmoid', cv=3)
    xgb_sigmoid.fit(X_train, y_train)
    joblib.dump(xgb_sigmoid, 'xgb_classifier.joblib')
    clf = joblib.load('xgb_classifier.joblib')

    import time

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

    start = time.time()
    # for i in range(10000):
    #     temp = SantoriniData(test_game, False).data

    data = SantoriniData(test_game, False).data
    data = data[1:]
    for i in range(100):
        win_prob = XGB_MODEL.predict_proba([data])[0][0]
    end = time.time()
    print(end - start)

    # y_class, y_prob = get_predictions(clf, X_train, y_train, X_test)
    # analyze_accuracy(y_test, y_prob, y_class)
    # plot_calibration(y_test, y_prob)
