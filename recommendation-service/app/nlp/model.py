from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def create_model():
    model = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("classifier", LogisticRegression()),
    ])

    return model