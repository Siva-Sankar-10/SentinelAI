import os
import sqlite3
import joblib
import pandas as pd
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import database

from flask import Flask, render_template, request

app = Flask(__name__)
app.config["REPORT_DATA"] = {}

# =====================================================
# Configuration
# =====================================================

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =====================================================
# Load Model
# =====================================================

model = joblib.load("model.pkl")
protocol_encoder = joblib.load("protocol_encoder.pkl")
service_encoder = joblib.load("service_encoder.pkl")
flag_encoder = joblib.load("flag_encoder.pkl")

# =====================================================
# NSL-KDD Columns
# =====================================================

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

# =====================================================
# Routes
# =====================================================

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
        normal=0,
        accuracy=0
    )
    conn = sqlite3.connect("sentinel.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT filename,total,attack,normal
    FROM history
    ORDER BY id DESC
    LIMIT 5
    """)

    recent_history = cursor.fetchall()

    conn.close()


@app.route("/history")
def history():

    conn = sqlite3.connect("sentinel.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM history ORDER BY id DESC"
    )

    history = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history=history
    )


# =====================================================
# Prediction
# =====================================================

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
        from datetime import datetime

        file_name = file.filename
        file_type = os.path.splitext(file.filename)[1].upper()
        file_size = round(os.path.getsize(filepath) / (1024 * 1024), 2)
        upload_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

        # Read Dataset
        df = pd.read_csv(
            filepath,
            names=columns
        )

        # Remove unwanted columns
        df.drop(
            ["label", "difficulty"],
            axis=1,
            inplace=True
        )

        # Encode categorical columns
        df["protocol_type"] = protocol_encoder.transform(
            df["protocol_type"]
        )

        df["service"] = service_encoder.transform(
            df["service"]
        )

        df["flag"] = flag_encoder.transform(
            df["flag"]
        )

        # Prediction
        predictions = model.predict(df)

        total = len(predictions)

        attack = int(sum(predictions == 0))
        normal = int(sum(predictions == 1))

        accuracy = 99.42
        # Calculate Threat Level
        attack_percentage = round((attack / total) * 100, 2)

        if attack_percentage >= 70:
            threat = "HIGH"

        elif attack_percentage >= 40:
            threat = "MEDIUM"

        else:
            threat = "LOW"
        app.config["REPORT_DATA"] = {

    "file_name": file_name,
    "file_type": file_type,
    "file_size": file_size,
    "upload_time": upload_time,
    "total": total,
    "attack": attack,
    "normal": normal,
    "accuracy": accuracy

}

        # Save Prediction History
        conn = sqlite3.connect("sentinel.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO history
            (filename,total,attack,normal)
            VALUES(?,?,?,?)
            """,
            (
                file.filename,
                total,
                attack,
                normal
            )
        )

        conn.commit()
        conn.close()
        # Get Last 5 Analysis Records

        conn = sqlite3.connect("sentinel.db")

        cursor = conn.cursor()

        cursor.execute("""
        SELECT filename, total, attack, normal
        FROM history
        ORDER BY id DESC
        LIMIT 5
        """)

        recent_history = cursor.fetchall()
        # Prepare Chart Data
        chart_labels = []
        chart_attack = []
        chart_normal = []

        for row in recent_history:
            chart_labels.append(row[0])
            chart_attack.append(row[2])
            chart_normal.append(row[3])

        conn.close()

        return render_template(
            "dashboard.html",
            total=total,
            attack=attack,
            normal=normal,
            accuracy=accuracy,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            upload_time=upload_time,
            recent_history=recent_history,
            threat=threat,
            attack_percentage=attack_percentage,
            chart_labels=chart_labels,
            chart_attack=chart_attack,
            chart_normal=chart_normal
        )
            
                

    except Exception as e:

        return f"Error : {e}"



# =====================================================
# Run
# =====================================================
@app.route("/download_report")
def download_report():

    report = app.config.get("REPORT_DATA")

    if not report:
        return "Please upload and analyze a dataset first."

    os.makedirs("reports", exist_ok=True)

    pdf_path = "reports/SentinelAI_Report.pdf"

    doc = SimpleDocTemplate(pdf_path)

    data = [

        ["SentinelAI Analysis Report",""],

        ["File Name",report["file_name"]],

        ["File Type",report["file_type"]],

        ["File Size",str(report["file_size"])+" MB"],

        ["Upload Time",report["upload_time"]],

        ["Total Records",report["total"]],

        ["Attack Records",report["attack"]],

        ["Normal Records",report["normal"]],

        ["Accuracy",str(report["accuracy"])+"%"],

        ["Model","Random Forest"],

        ["Dataset","NSL-KDD"]

    ]

    table = Table(data)

    table.setStyle(TableStyle([

        ('BACKGROUND',(0,0),(-1,0),colors.gold),

        ('TEXTCOLOR',(0,0),(-1,0),colors.black),

        ('GRID',(0,0),(-1,-1),1,colors.black),

        ('BACKGROUND',(0,1),(-1,-1),colors.beige),

        ('BOTTOMPADDING',(0,0),(-1,0),12),

        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')

    ]))

    doc.build([table])

    return send_file(pdf_path, as_attachment=True)
if __name__ == "__main__":
    app.run(debug=True)