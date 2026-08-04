from flask import render_template
import app as flask_app

# Render the dashboard template through Flask's engine (provides url_for, tojson, etc.)
with flask_app.app.test_request_context():
    try:
        html = render_template(
            "dashboard.html",
            total=100,
            attack=40,
            normal=60,
            accuracy=99.42,
            threat="MEDIUM",
            file_name="test.csv",
            file_type="CSV",
            file_size=1.5,
            upload_time="01-01-2026 10:00:00",
            recent_history=[("test.csv", 100, 40, 60)],
            chart_labels=["test.csv"],
            chart_attack=[40],
            chart_normal=[60],
        )
        print("DASHBOARD TEMPLATE RENDERED OK, length:", len(html))
    except Exception:
        import traceback
        traceback.print_exc()

# Now show exactly which line in app.py fails
print("=" * 60)
print("Locating the failing line in app.py /dashboard route...")
with open("app.py", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if "file_name" in line and "SELECT" in "".join(lines[max(0, i-3):i]):
        print(f"app.py line {i}: {line.rstrip()}")
    if "SELECT file_name" in line:
        print(f"app.py line {i}: {line.rstrip()}")

