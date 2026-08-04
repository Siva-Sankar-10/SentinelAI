import joblib
import pandas as pd

# Load everything
saved = joblib.load("sentinel_model.pkl")

model = saved["model"]
protocol_encoder = saved["protocol_encoder"]
service_encoder = saved["service_encoder"]
flag_encoder = saved["flag_encoder"]
feature_names = saved["feature_names"]


def safe_transform(series, encoder):

    values = series.astype(str)
    known_values = set(encoder.classes_)

    values = values.map(
        lambda value: value if value in known_values else encoder.classes_[0]
    )

    return encoder.transform(values)


def predict_dataset(filepath):

    df = pd.read_csv(filepath, header=None)
    df.columns = [
        "duration","protocol_type","service","flag","src_bytes","dst_bytes",
        "land","wrong_fragment","urgent","hot","num_failed_logins","logged_in",
        "num_compromised","root_shell","su_attempted","num_root",
        "num_file_creations","num_shells","num_access_files",
        "num_outbound_cmds","is_host_login","is_guest_login","count",
        "srv_count","serror_rate","srv_serror_rate","rerror_rate",
        "srv_rerror_rate","same_srv_rate","diff_srv_rate",
        "srv_diff_host_rate","dst_host_count","dst_host_srv_count",
        "dst_host_same_srv_rate","dst_host_diff_srv_rate",
        "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate",
        "dst_host_serror_rate","dst_host_srv_serror_rate",
        "dst_host_rerror_rate","dst_host_srv_rerror_rate",
        "label","difficulty"
    ]

    df = df.drop(["label", "difficulty"], axis=1, errors="ignore")

    df["protocol_type"] = safe_transform(df["protocol_type"], protocol_encoder)
    df["service"] = safe_transform(df["service"], service_encoder)
    df["flag"] = safe_transform(df["flag"], flag_encoder)

    df = df.reindex(columns=feature_names, fill_value=0)

    predictions = model.predict(df)

    return predictions