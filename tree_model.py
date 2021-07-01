from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import pandas as pd


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
    rf = RandomForestClassifier(n_estimators=200, random_state=0)
    xgb = XGBClassifier(booster='gbtree', random_state=0, use_label_encoder=False,
                        eval_metric='logloss', n_estimators=200, max_depth=3, gamma=0.1, colsample_bytree=1,
                        subsample=1, min_child_weight=3)
    df = pd.read_csv('game_list.csv', header=None)
    y = df.iloc[:, 0]
    X = df.iloc[:, 1:]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    # params = {'max_depth': [3], 'gamma': [0.1], 'colsample_bytree': [1.0], 'subsample': [1.0],
    #           'min_child_weight': [3]}
    # xgb_cv = GridSearchCV(xgb, param_grid=params, cv=5, verbose=-1)

    xgb.fit(X_train, y_train)
    #print("best estimator:", xgb_cv.best_estimator_)
    xgb_sigmoid = CalibratedClassifierCV(xgb, method='sigmoid')
    y_class, y_prob = get_predictions(xgb_sigmoid, X_train, y_train, X_test)
    for i in y_prob:
        print(i)
    analyze_accuracy(y_test, y_prob, y_class)
    plot_calibration(y_test, y_prob)
