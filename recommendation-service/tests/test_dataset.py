from app.nlp.dataset import load_dataset, validate_dataset


def test_dataset_is_valid(dataset_path):
    validate_dataset(dataset_path)


def test_dataset_has_required_intents():
    _, _, df = load_dataset()
    required = {
        "device_security",
        "network_security",
        "malware_protection",
        "password_security",
        "privacy",
        "general_query",
    }
    assert required.issubset(set(df["intent"].unique()))


def test_dataset_has_polish_and_english():
    _, _, df = load_dataset()
    assert {"pl", "en"}.issubset(set(df["language"].unique()))


def test_dataset_minimum_size_per_intent():
    """Each intent must have at least 15 examples to give the classifier
    any chance of generalising.
    """
    _, _, df = load_dataset()
    counts = df["intent"].value_counts()
    below = counts[counts < 15]
    assert below.empty, f"Intents with too few examples: {below.to_dict()}"


def test_dataset_balanced_languages_per_intent():
    """Both PL and EN must be represented for each non-general intent."""
    _, _, df = load_dataset()
    for intent, group in df.groupby("intent"):
        if intent == "general_query":
            continue
        languages = set(group["language"])
        assert "pl" in languages, f"{intent} has no Polish examples"
        assert "en" in languages, f"{intent} has no English examples"


def test_dataset_no_duplicates():
    _, _, df = load_dataset()
    assert df["text"].duplicated().sum() == 0


def test_dataset_no_empty_text():
    _, _, df = load_dataset()
    assert (df["text"].str.strip() == "").sum() == 0