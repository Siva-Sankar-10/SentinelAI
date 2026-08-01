import os
import joblib
import pandas as pd
import sqlite3
import database
from flask import Flask, render_template, request

app = Flask(__name__)

# ============================================
# Configuration
# ============================================

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================
# Load Model & Encoders
# ============================================

model = joblib.load("model.pkl")
protocol_encoder = joblib.load("protocol_encoder.pkl")
service_encoder = joblib.load("service_encoder.pkl")
flag_encoder = joblib.load("flag_encoder.pkl")

# ============================================
# NSL-KDD Column Names
# ============================================

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

# ============================================
# Routes
# ============================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/dashboard")
def dashboard():
    return render_template(
        "dashboard.html",
        total=0,
        attack=0,
        normal=0
    )
@app.route("/history")
def history():

    conn = sqlite3.connect("sentinel.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM history ORDER BY id DESC")

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history=data
    )
# ============================================
# Prediction
# ============================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        if "file" not in request.files:
            return "No file uploaded."

        file = request.files["file"]

        if file.filename == "":
            return "Please choose a file."

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        # Read uploaded NSL-KDD dataset
        df = pd.read_csv(filepath, names=columns)

        # Remove unwanted columns
        df.drop(["label", "difficulty"], axis=1, inplace=True)

        # Encode categorical columns
        df["protocol_type"] = protocol_encoder.transform(df["protocol_type"])
        df["service"] = service_encoder.transform(df["service"])
        df["flag"] = flag_encoder.transform(df["flag"])

        # Prediction
        predictions = model.predict(df)

        total = len(predictions)

        attack = sum(predictions == 0)
        normal = sum(predictions == 1)

        accuracy = 99.42
conn = sqlite3.connect("sentinel.db")

cursor = conn.cursor()

cursor.execute(

"""
INSERT INTO history
(filename,total,attack,normal)
VALUES(?,?,?,?)
""",

(file.filename,total,attack,normal)

)

conn.commit()

conn.close()
        return render_template(
            "dashboard.html",
            total=total,
            attack=attack,
            normal=normal,
            accuracy=accuracy
        )

    except Exception as e:
        return f"Error : {e}"

# ============================================
# Run
# ============================================

if __name__ == "__main__":
    app.run(debug=True)