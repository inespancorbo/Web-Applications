import streamlit as st
import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import plot_confusion_matrix, plot_roc_curve, plot_precision_recall_curve
from sklearn.metrics import precision_score, recall_score

URL = 'https://datahub.io/machine-learning/mushroom/r/mushroom.csv'


@st.cache(persist=True)
def load_data():
    data = pd.read_csv(URL)

    # drop one row with missing value
    data.dropna(inplace=True)

    label = LabelEncoder()
    for col in data.columns:
        data[col] = label.fit_transform(data[col])
    return data


@st.cache(persist=True)
def split(data):
    y = data['class']
    x = data.drop('class', axis=1)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    return x_train, x_test, y_train, y_test


def main():

    def plot_metrics(metrics_list):
        if 'Confusion Matrix' in metrics_list:
            st.subheader('Confusion Matrix')
            plot_confusion_matrix(model, x_test, y_test, display_labels=['edible', 'poisonous'])
            st.pyplot()

        if 'ROC Curve' in metrics_list:
            st.subheader('ROC Curve')
            plot_roc_curve(model, x_test, y_test)
            st.pyplot()

        if 'Precision-Recall Curve' in metrics_list:
            st.subheader('Precision-Recall Curve')
            plot_precision_recall_curve(model, x_test, y_test)
            st.pyplot()

    st.title("Binary Classification Web App")
    st.sidebar.title("Binary Classification Web App")
    st.markdown("Are your mushrooms edible or poisonous? 🍄 ")
    st.sidebar.markdown("Are your mushrooms edible or poisonous? 🍄 ")

    data = load_data()

    if st.sidebar.checkbox('Show raw data', False):
        st.subheader('Mushroom Data Set (Classification)')
        st.write(data)

    x_train, x_test, y_train, y_test = split(data)
    st.sidebar.subheader('Choose Classifier')
    classifier = st.sidebar.selectbox('Classifier', (
        'Support Vector Machines (SVM)', 'Logistic Regression', 'Random Forest'
    ))

    if classifier == 'Support Vector Machines (SVM)':
        st.sidebar.subheader('Model Hyperparameters')
        C = st.sidebar.number_input('C (Regularization parameter)', 0.01, 10.0, step=0.01, key='C')
        kernel = st.sidebar.radio('Kernel', ('rbf', 'linear'), key='kernel')
        gamma = st.sidebar.radio('Gamma (Kernel coefficient)', ('scale', 'auto'), key='gamma')

        metrics = st.sidebar.multiselect('What metrics to plot?', (
            'Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve'
        ))

        if st.sidebar.button('Classify', key='classify'):
            st.subheader('Support Vector Machines (SVM) Results')
            model = SVC(C=C, kernel=kernel, gamma=gamma)
            model.fit(x_train, y_train)
            y_pred = model.predict(x_test)
            st.write('Accuracy: ', model.score(x_test, y_test).round(2))
            st.write('Recall: ', recall_score(y_test, y_pred, labels=['edible', 'poisonous']).round(2))
            st.write('Precision: ', precision_score(y_test, y_pred, labels=['edible', 'poisonous']).round(2))
            plot_metrics(metrics)

    if classifier == 'Logistic Regression':
        st.sidebar.subheader('Model Hyperparameters')
        C = st.sidebar.number_input('C (Regularization parameter)', 0.01, 10.0, step=0.01, key='C')
        solver = st.sidebar.selectbox('Optimizer', (
            'newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'
        ))

        metrics = st.sidebar.multiselect('What metrics to plot?', (
            'Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve'
        ))

        if st.sidebar.button('Classify', key='classify'):
            st.subheader('Logistic Regression Results')
            model = LogisticRegression(C=C, solver=solver)
            model.fit(x_train, y_train)
            y_pred = model.predict(x_test)
            st.write('Accuracy: ', model.score(x_test, y_test).round(2))
            st.write('Recall: ', recall_score(y_test, y_pred, labels=['edible', 'poisonous']).round(2))
            st.write('Precision: ', precision_score(y_test, y_pred, labels=['edible', 'poisonous']).round(2))
            plot_metrics(metrics)

    if classifier == 'Random Forest':
        st.sidebar.subheader('Model Hyperparameters')
        n_estimators = st.sidebar.slider('The number of trees in the forest', 1, 5000)
        max_depth = st.sidebar.number_input('The maximum depth of the tree', 1, 20, step=1)
        bootstrap = st.sidebar.radio('Bootstrap samples when building trees?', ('True', 'False'))
        max_features = st.sidebar.selectbox('Number of features to consider when looking for best split',
                                            ('sqrt', 'log2', 'None'))

        metrics = st.sidebar.multiselect('What metrics to plot?', (
            'Confusion Matrix', 'ROC Curve', 'Precision-Recall Curve'
        ))

        if st.sidebar.button('Classify', key='classify'):
            st.subheader('Random Forest Results')
            model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, bootstrap=bootstrap, max_features=max_features, n_jobs=-1)
            model.fit(x_train, y_train)
            y_pred = model.predict(x_test)
            st.write('Accuracy: ', model.score(x_test, y_test).round(2))
            st.write('Recall: ', recall_score(y_test, y_pred, labels=['edible', 'poisonous']).round(2))
            st.write('Precision: ', precision_score(y_test, y_pred, labels=['edible', 'poisonous']).round(2))
            plot_metrics(metrics)


if __name__ == '__main__':
    main()


