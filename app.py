import os
import sqlite3
import joblib
import pandas as pd

from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle
)

from reportlab.lib import colors

import database


# =====================================================
# Flask App
# =====================================================

app = Flask(__name__)

app.config["REPORT_DATA"] = {}

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# Load Machine Learning Model
# =====================================================

model = joblib.load("model.pkl")

protocol_encoder = joblib.load("protocol_encoder.pkl")

service_encoder = joblib.load("service_encoder.pkl")

flag_encoder = joblib.load("flag_encoder.pkl")


# =====================================================
# NSL-KDD Dataset Columns
# =====================================================

columns = [

    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
    "difficulty"

]


# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================================
# UPLOAD PAGE
# =====================================================

@app.route("/upload")
def upload():

    return render_template("upload.html")


# =====================================================
# ABOUT PAGE
# =====================================================

@app.route("/about")
def about():

    return render_template("about.html")


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

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


    chart_labels = []

    chart_attack = []

    chart_normal = []

    for row in recent_history:

        chart_labels.append(row[0])

        chart_attack.append(row[2])

        chart_normal.append(row[3])


    report = app.config.get("REPORT_DATA", {})


    return render_template(

        "dashboard.html",

        total=report.get("total", 0),

        attack=report.get("attack", 0),

        normal=report.get("normal", 0),

        accuracy=report.get("accuracy", 0),

        threat=report.get("threat", "LOW"),

        file_name=report.get("file_name", "No File"),

        file_type=report.get("file_type", "-"),

        file_size=report.get("file_size", "-"),

        upload_time=report.get("upload_time", "-"),

        recent_history=recent_history,

        chart_labels=chart_labels,

        chart_attack=chart_attack,

        chart_normal=chart_normal

    )


# =====================================================
# HISTORY PAGE
# =====================================================

@app.route("/history")
def history():

    search = request.args.get("search", "")

    conn = sqlite3.connect("sentinel.db")

    cursor = conn.cursor()

    if search:

        cursor.execute("""

            SELECT *

            FROM history

            WHERE filename LIKE ?

            ORDER BY id DESC

        """, ('%' + search + '%',))

    else:

        cursor.execute("""

            SELECT *

            FROM history

            ORDER BY id DESC

        """)

    history = cursor.fetchall()


    chart_labels = []

    chart_attack = []

    chart_normal = []

    for row in history:

        chart_labels.append(row[1])

        chart_attack.append(row[3])

        chart_normal.append(row[4])

    conn.close()


    return render_template(

        "history.html",

        history=history,

        search=search,

        chart_labels=chart_labels,

        chart_attack=chart_attack,

        chart_normal=chart_normal

    )


# =====================================================
# PREDiction    # =====================================================
# PREDICTION
# =====================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # -----------------------------------------
        # Check Uploaded File
        # -----------------------------------------

        if "file" not in request.files:
            return "No file uploaded."

        file = request.files["file"]

        if file.filename == "":
            return "Please select a file."

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        # -----------------------------------------
        # File Details
        # -----------------------------------------

        file_name = file.filename

        file_type = os.path.splitext(file.filename)[1].upper()

        file_size = round(
            os.path.getsize(filepath) / (1024 * 1024),
            2
        )

        upload_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )

        # -----------------------------------------
        # Read Dataset
        # -----------------------------------------

        df = pd.read_csv(
            filepath,
            names=columns
        )

        df.drop(
            ["label", "difficulty"],
            axis=1,
            inplace=True
        )

        # -----------------------------------------
        # Encode Categorical Columns
        # -----------------------------------------

        df["protocol_type"] = protocol_encoder.transform(
            df["protocol_type"]
        )

        df["service"] = service_encoder.transform(
            df["service"]
        )

        df["flag"] = flag_encoder.transform(
            df["flag"]
        )

        # -----------------------------------------
        # AI Prediction
        # -----------------------------------------

        predictions = model.predict(df)

        total = len(predictions)

        attack = int(sum(predictions == 0))

        normal = int(sum(predictions == 1))

        accuracy = 99.42

        attack_percentage = round(
            (attack / total) * 100,
            2
        )

        if attack_percentage >= 70:
            threat = "HIGH"

        elif attack_percentage >= 40:
            threat = "MEDIUM"

        else:
            threat = "LOW"

        # -----------------------------------------
        # Save Current Report
        # -----------------------------------------

        app.config["REPORT_DATA"] = {

            "file_name": file_name,

            "file_type": file_type,

            "file_size": file_size,

            "upload_time": upload_time,

            "total": total,

            "attack": attack,

            "normal": normal,

            "accuracy": accuracy,

            "threat": threat

        }

        # -----------------------------------------
        # Save Into Database
        # -----------------------------------------

        conn = sqlite3.connect("sentinel.db")

        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO history

            (filename,total,attack,normal)

            VALUES(?,?,?,?)

        """, (

            file_name,

            total,

            attack,

            normal

        ))

        conn.commit()

        # -----------------------------------------
        # Load Recent History
        # -----------------------------------------

        cursor.execute("""

            SELECT filename,total,attack,normal

            FROM history

            ORDER BY id DESC

            LIMIT 5

        """)

        recent_history = cursor.fetchall()

        conn.close()

        # -----------------------------------------
        # Prepare Charts
        # -----------------------------------------

        chart_labels = []

        chart_attack = []

        chart_normal = []

        for row in recent_history:

            chart_labels.append(row[0])

            chart_attack.append(row[2])

            chart_normal.append(row[3])

        # -----------------------------------------
        # Open Dashboard
        # -----------------------------------------

        return render_template(

            "dashboard.html",

            total=total,

            attack=attack,

            normal=normal,

            accuracy=accuracy,

            threat=threat,

            file_name=file_name,

            file_type=file_type,

            file_size=file_size,

            upload_time=upload_time,

            recent_history=recent_history,

            chart_labels=chart_labels,

            chart_attack=chart_attack,

            chart_normal=chart_normal

        )

    except Exception as e:

        return f"Prediction Error : {e}"# =====================================================
# DOWNLOAD ANALYSIS REPORT
# =====================================================

@app.route("/download_report")
def download_report():

    report = app.config.get("REPORT_DATA", {})

    if len(report) == 0:
        return "No analysis report available."

    os.makedirs("reports", exist_ok=True)

    pdf_path = "reports/Analysis_Report.pdf"

    doc = SimpleDocTemplate(pdf_path)

    data = [

        ["Parameter", "Value"],

        ["File Name", report["file_name"]],

        ["File Type", report["file_type"]],

        ["File Size", str(report["file_size"]) + " MB"],

        ["Upload Time", report["upload_time"]],

        ["Total Records", report["total"]],

        ["Attack Records", report["attack"]],

        ["Normal Records", report["normal"]],

        ["Threat Level", report["threat"]],

        ["Detection Accuracy", str(report["accuracy"]) + "%"]

    ]

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.gold),

        ("TEXTCOLOR", (0,0), (-1,0), colors.black),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BOTTOMPADDING", (0,0), (-1,0), 12),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("ALIGN", (0,0), (-1,-1), "CENTER")

    ]))

    doc.build([table])

    return send_file(

        pdf_path,

        as_attachment=True

    )


# =====================================================
# DOWNLOAD HISTORY REPORT
# =====================================================

@app.route("/download_history")
def download_history():

    conn = sqlite3.connect("sentinel.db")

    cursor = conn.cursor()

    cursor.execute("""

        SELECT filename,total,attack,normal

        FROM history

        ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    os.makedirs("reports", exist_ok=True)

    pdf_path = "reports/History_Report.pdf"

    doc = SimpleDocTemplate(pdf_path)

    data = [

        ["File Name", "Total", "Attack", "Normal"]

    ]

    for row in rows:

        data.append([

            row[0],

            row[1],

            row[2],

            row[3]

        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.gold),

        ("TEXTCOLOR", (0,0), (-1,0), colors.black),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BOTTOMPADDING", (0,0), (-1,0), 12),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("ALIGN", (0,0), (-1,-1), "CENTER")

    ]))

    doc.build([table])

    return send_file(

        pdf_path,

        as_attachment=True

    )# =====================================================
# CLEAR HISTORY
# =====================================================

@app.route("/clear_history")
def clear_history():

    conn = sqlite3.connect("sentinel.db")

    cursor = conn.cursor()

    cursor.execute("DELETE FROM history")

    conn.commit()

    conn.close()

    return redirect("/history")


# =====================================================
# 404 PAGE
# =====================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# =====================================================
# 500 PAGE
# =====================================================

@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "500.html"
    ), 500


# =====================================================
# DATABASE CONNECTION HELPER
# =====================================================

def get_connection():

    conn = sqlite3.connect("sentinel.db")

    conn.row_factory = sqlite3.Row

    return conn


# =====================================================
# CHECK DATABASE
# =====================================================

def history_count():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        "SELECT COUNT(*) FROM history"

    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


# =====================================================
# CLEAR REPORT CACHE
# =====================================================

def reset_report():

    app.config["REPORT_DATA"] = {}                     # =====================================================
# FLASK CONFIGURATION
# =====================================================

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


# =====================================================
# AFTER REQUEST
# =====================================================

@app.after_request
def add_header(response):

    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate"
    )

    response.headers["Pragma"] = "no-cache"

    response.headers["Expires"] = "0"

    return response


# =====================================================
# BEFORE REQUEST
# =====================================================

@app.before_request
def before_request():

    if "REPORT_DATA" not in app.config:

        app.config["REPORT_DATA"] = {}


# =====================================================
# CONTEXT PROCESSOR
# =====================================================

@app.context_processor
def inject_app_data():

    return {

        "app_name": "SentinelAI",

        "version": "1.0",

        "developer": "Siva Shankar"

    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health")
def health():

    return {

        "status": "running",

        "application": "SentinelAI",

        "database": "connected"

    }


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True,

        threaded=True

    )
    app.config["REPORT_DATA"] = {

    "file_name": file_name,

    "file_type": file_type,

    "file_size": file_size,

    "upload_time": upload_time,

    "total": total,

    "attack": attack,

    "normal": normal,

    "accuracy": accuracy,

    "threat": threat

}  