import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

if __name__ == "__main__":
    # Load the training data
    train_data = pd.read_csv('iris_train.csv')
    X_train = train_data.drop('target', axis=1)
    y_train = train_data['target']

    # Train a RandomForestClassifier
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)

    # Save the trained model to a file
    with open('model.pkl', 'wb') as model_file:
        pickle.dump(clf, model_file)

    print("Training complete.")

