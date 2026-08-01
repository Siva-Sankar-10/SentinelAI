import pandas as pd
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ---------------------------------------------------
# Column Names
# ---------------------------------------------------

columns = [
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

# ---------------------------------------------------
# Load Dataset
# ---------------------------------------------------

print("Loading Dataset...")

df = pd.read_csv(
    "dataset/KDDTrain+.txt",
    names=columns
)

print("Dataset Loaded Successfully!")

print("Dataset Shape :", df.shape)

# ---------------------------------------------------
# Remove Difficulty Column
# ---------------------------------------------------

df.drop("difficulty", axis=1, inplace=True)

# ---------------------------------------------------
# Convert Labels
# Normal = normal
# All attacks = attack
# ---------------------------------------------------

df["label"] = df["label"].apply(
    lambda x: "normal" if x == "normal" else "attack"
)

# ---------------------------------------------------
# Encode Categorical Columns
# ---------------------------------------------------

protocol_encoder = LabelEncoder()
service_encoder = LabelEncoder()
flag_encoder = LabelEncoder()
label_encoder = LabelEncoder()

df["protocol_type"] = protocol_encoder.fit_transform(df["protocol_type"])
df["service"] = service_encoder.fit_transform(df["service"])
df["flag"] = flag_encoder.fit_transform(df["flag"])
df["label"] = label_encoder.fit_transform(df["label"])

print("\nEncoding Completed!")

# ---------------------------------------------------
# Split Features and Target
# ---------------------------------------------------

X = df.drop("label", axis=1)
y = df["label"]

print("Feature Shape :", X.shape)
print("Target Shape :", y.shape)

# ---------------------------------------------------
# Split Train & Test
# ---------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training Samples :", len(X_train))
print("Testing Samples :", len(X_test))

# ---------------------------------------------------
# Train Random Forest
# ---------------------------------------------------

print("\nTraining Model...")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Model Training Completed!")

# ---------------------------------------------------
# Prediction
# ---------------------------------------------------

y_pred = model.predict(X_test)

# ---------------------------------------------------
# Accuracy
# ---------------------------------------------------

accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("MODEL ACCURACY")
print("==============================")
print(f"Accuracy : {accuracy*100:.2f}%")

# ---------------------------------------------------
# Classification Report
# ---------------------------------------------------

print("\n==============================")
print("CLASSIFICATION REPORT")
print("==============================")
print(classification_report(y_test, y_pred))

# ---------------------------------------------------
# Confusion Matrix
# ---------------------------------------------------

print("\n==============================")
print("CONFUSION MATRIX")
print("==============================")
print(confusion_matrix(y_test, y_pred))

# ---------------------------------------------------
# Feature Importance
# ---------------------------------------------------

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

print("\nTop 10 Important Features")
print(importance.head(10))

# ---------------------------------------------------
# Save Model
# ---------------------------------------------------
# ---------------------------------------------------
# Save Everything
# ---------------------------------------------------

saved_objects = {
    "model": model,
    "protocol_encoder": protocol_encoder,
    "service_encoder": service_encoder,
    "flag_encoder": flag_encoder,
    "feature_names": X.columns.tolist()
}

joblib.dump(saved_objects, "sentinel_model.pkl")

print("\n================================")
print("SentinelAI Model Saved Successfully!")
print("File : sentinel_model.pkl")
print("================================")# ---------------------------------------------------
# Save Model and Encoders
# ---------------------------------------------------

# ---------------------------------------------------
# Save Model
# ---------------------------------------------------

joblib.dump(model, "model.pkl")

joblib.dump(protocol_encoder, "protocol_encoder.pkl")

joblib.dump(service_encoder, "service_encoder.pkl")

joblib.dump(flag_encoder, "flag_encoder.pkl")

print("\n===================================")
print("Model Saved Successfully!")
print("===================================")
print("model.pkl")
print("protocol_encoder.pkl")
print("service_encoder.pkl")
print("flag_encoder.pkl")