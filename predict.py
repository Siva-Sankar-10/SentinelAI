import joblib
import pandas as pd

# Load everything
saved = joblib.load("sentinel_model.pkl")

model = saved["model"]
protocol_encoder = saved["protocol_encoder"]
service_encoder = saved["service_encoder"]
flag_encoder = saved["flag_encoder"]
feature_names = saved["feature_names"]


def predict_dataset(filepath):

    df = pd.read_csv(filepath)

    # Encode categorical columns
    df["protocol_type"] = protocol_encoder.transform(df["protocol_type"])
    df["service"] = service_encoder.transform(df["service"])
    df["flag"] = flag_encoder.transform(df["flag"])

    # Keep only training features
    df = df[feature_names]

    predictions = model.predict(df)

    return predictions