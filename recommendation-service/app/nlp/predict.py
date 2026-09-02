import joblib


MODEL_PATH = "/app/nlp/model.joblib"


model = joblib.load(MODEL_PATH)


def predict_intent(text: str):

    prediction = model.predict([text])[0]

    probabilities = model.predict_proba([text])[0]

    classes = model.classes_

    return prediction, probabilities, classes


# Uruchamiamy testy tylko wtedy,
# gdy plik jest uruchomiony bezpośrednio.
if __name__ == "__main__":

    new_texts = [
        "jak zabezpieczyć moje wifi",
        "chcę ochronić router",
        "mój laptop jest niezabezpieczony",
        "mam wirusa",
        "jak pozbyć się malware",
    ]

    print("=== NEW TEXTS ===")

    for text in new_texts:

        prediction, probabilities, classes = predict_intent(text)

        print(f"\nText: {text}")
        print(f"Predicted: {prediction}")

        print("Probabilities:")

        for class_name, probability in zip(
            classes,
            probabilities,
        ):
            print(
                f"  {class_name}: "
                f"{probability:.3f}"
            )