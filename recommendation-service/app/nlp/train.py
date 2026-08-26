import joblib

from sklearn.metrics import (
    accuracy_score,
    classification_report,
)

from nlp.dataset import load_dataset
from nlp.model import create_model


MODEL_PATH = "/app/nlp/model.joblib"


def train_model():

    X_train, X_test, y_train, y_test = load_dataset()

    model = create_model()

    model.fit(X_train, y_train)

    # Zapisujemy wytrenowany model do pliku.
    joblib.dump(model, MODEL_PATH)

    print(
        f"Model saved to: {MODEL_PATH}"
    )

    return model, X_test, y_test


if __name__ == "__main__":

    model, X_test, y_test = train_model()

    predictions = model.predict(X_test)

    print("=== TEST DATA ===")

    for text, actual, predicted in zip(
        X_test,
        y_test,
        predictions,
    ):
        print(f"Text: {text}")
        print(f"Actual: {actual}")
        print(f"Predicted: {predicted}")
        print()

    print("Accuracy:")

    print(
        accuracy_score(
            y_test,
            predictions,
        )
    )

    print("\nClassification report:")

    print(
        classification_report(
            y_test,
            predictions,
        )
    )