import pandas as pd

from sklearn.model_selection import train_test_split


DATASET_PATH = "/app/nlp/data/intents.csv"


def load_dataset():
    df = pd.read_csv(DATASET_PATH)

    X = df["text"]
    y = df["intent"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    return X_train, X_test, y_train, y_test