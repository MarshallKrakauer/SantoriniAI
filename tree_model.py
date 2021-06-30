from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import pandas as pd


def get_predictions(model, X_train, y_train, X_test):
    model.fit(X_train, y_train)
    y_pred_class = model.predict(X_test)
    y_pred_prob = model.predict_proba(X_test)
    y_pred_prob = [elem[1] for elem in y_pred_prob]

    return y_pred_class, y_pred_prob


def analyze_accuracy(y_test, y_pred_prob, y_pred_class):
    naive_pred = [0.5 for i in range(len(y_pred_class))]

    ns_auc = roc_auc_score(y_test, naive_pred)
    md_auc = roc_auc_score(y_test, y_pred_prob)
    print('No Skill: ROC AUC=%.3f' % (ns_auc))
    print('Model   : ROC AUC=%.3f' % (md_auc))

    ns_fpr, ns_tpr, _ = roc_curve(y_test, naive_pred)
    lr_fpr, lr_tpr, _ = roc_curve(y_test, y_pred_prob)


def plot_calibration(y_test, y_prob):
    fop, mpv = calibration_curve(y_test, y_prob, n_bins=10, normalize=True)
    # plot perfectly calibrated
    plt.plot([0, 1], [0, 1], linestyle='--')
    # plot model reliability
    plt.plot(mpv, fop, marker='.')
    plt.show()


rf = RandomForestClassifier(n_estimators=200)
xgb = XGBClassifier(booster='gbtree', random_state=0, use_label_encoder=False, eval_metric='logloss')
df = pd.read_csv('game_list.csv', header=None)
y = df.iloc[:, 0]
X = df.iloc[:, 1:]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
rf.fit(X_train, y_train)

rf_sigmoid = CalibratedClassifierCV(rf, method='sigmoid')
y_class, y_prob = get_predictions(rf_sigmoid, X_train, y_train, X_test)
analyze_accuracy(y_test, y_prob, y_class)
plot_calibration(y_test, y_prob)
