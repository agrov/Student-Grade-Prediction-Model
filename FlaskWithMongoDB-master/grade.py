def predict_class(X_test):
    import numpy as np # linear algebra
    import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
    from xgboost import XGBClassifier
    edm = pd.read_csv(r'E:\Beuth_Applications\Data\FlaskWithMongoDB-master\templates\Edu.csv')
    X_train = edm.drop('Class', axis=1)
    y_train = edm['Class']

    # Encoding our categorical columns in X
    labelEncoder = LabelEncoder()
    cat_columns = X_train.dtypes.pipe(lambda x: x[x == 'object']).index
    for col in cat_columns:
        X_train[col] = labelEncoder.fit_transform(X_train[col])
    
    cat_columns_t = X_test.dtypes.pipe(lambda x: x[x == 'object']).index
    for col in cat_columns_t:
        X_test[col] = labelEncoder.fit_transform(X_test[col])


    xgb = XGBClassifier(seed=52)
    pred = xgb.fit(X_train, y_train).predict(X_test)
    return pred[0]