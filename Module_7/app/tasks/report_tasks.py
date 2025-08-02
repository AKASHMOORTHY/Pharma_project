from app.celery_utils import celery_app
import os
import csv
from jinja2 import Template
# from weasyprint import HTML
from xhtml2pdf import pisa
from datetime import datetime
import uuid
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta
from typing import Dict, Any

load_dotenv()  # load .env

print("✅ .env Loaded")
print("SMTP_PORT:", os.getenv("SMTP_PORT"))


EMAIL_USER = os.getenv("SMTP_USER")
EMAIL_PASS = os.getenv("SMTP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_HOST = os.getenv("SMTP_HOST")
smtp_port_env = os.getenv("SMTP_PORT")

if smtp_port_env is None:
    raise ValueError("SMTP_PORT is missing from .env file")

SMTP_PORT = int(smtp_port_env)

os.makedirs("generated_reports", exist_ok=True)

@celery_app.task(name="app.tasks.report_tasks.generate_report")
def generate_report(report_name: str, format: str, start_date: str = None, end_date: str = None):
    try:
        print(f"🔧 Generating report: {report_name}, {format}")
        # data = [
        # {"date": "2025-07-01", "shift": "A", "batches": 10},
        # {"date": "2025-07-02", "shift": "B", "batches": 15},
        # ]

        db = SessionLocal()
        try:
            filters = {}
            start_date = filters.get("start_date")
            end_date = filters.get("end_date")
            product_line = filters.get("product_line")  # Optional extra filter
            # # Example: fetch all production batches
            query = db.query(models.ProductionBatch)
            if start_date:
                query = query.filter(models.ProductionBatch.production_date >= start_date)
            if end_date:
                query = query.filter(models.ProductionBatch.production_date <= end_date)
            # After start_date and end_date filters
            product_line = filters.get("product_line") if filters else None
            if product_line:
                query = query.filter(models.ProductionBatch.product_line == product_line)  # if you add this field

            db_data = query.all()

            # db_data = db.query(models.ProductionBatch).all()
            # Convert ORM objects to dicts for reporting
            data = [
                {
                    "date": batch.production_date.strftime("%Y-%m-%d"),
                    "shift": batch.shift,
                    "status": batch.status,
                    "duration": batch.duration,
                }
                for batch in db_data
            ]
        finally:
            db.close()

        # Standardize format to lowercase
        format = format.lower()
        file_id = f"{report_name}_{uuid.uuid4().hex[:6]}"
        file_path = f"generated_reports/{file_id}.{format}"

        print("📁 Writing file:", file_path)
        # Save as CSV or PDF
        if format == "csv":
            with open(file_path, mode="w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

        elif format == "pdf":
            html_template = """
            <html>
            <head><style>table, th, td { border: 1px solid black; border-collapse: collapse; padding: 6px; }</style></head>
            <body>
            <h2>{{ title }}</h2>
            <table>
                <tr>
                    {% for key in data[0].keys() %}
                    <th>{{ key }}</th>
                    {% endfor %}
                </tr>
                {% for row in data %}
                <tr>
                    {% for cell in row.values() %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </table>
            </body></html>
            """
            template = Template(html_template)
            rendered = template.render(title=report_name, data=data)

            with open(file_path, "w+b") as result_file:
                pisa_status = pisa.CreatePDF(rendered, dest=result_file)

            if pisa_status.err:
                print(f"[PDF ERROR] Failed to generate PDF for {file_path}")
                return {"status": "failed", "reason": "PDF generation failed"}

        # Email the report
        print("📤 Sending email to:", EMAIL_TO)
        try:
            if not os.path.isfile(file_path):
                print(f"[EMAIL FAILED] Report file not found: {file_path}")
                return {"status": "failed", "reason": f"Report file not found: {file_path}"}

            msg = EmailMessage()
            msg["Subject"] = f"{report_name} Generated"
            msg["From"] = EMAIL_USER
            msg["To"] = EMAIL_TO
            msg.set_content(f"Attached is the {report_name} you requested.")

            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
                mime_type = "application/pdf" if format == "pdf" else "text/csv"
                msg.add_attachment(file_data, maintype=mime_type.split("/")[0], subtype=mime_type.split("/")[1], filename=file_name)

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_USER, EMAIL_PASS)
                smtp.send_message(msg)

            print(f"[EMAIL SENT] {file_name} sent to {EMAIL_TO}")
        except Exception as e:
            print(f"[EMAIL FAILED] Error sending email: {str(e)}")
  
        print("✅ Task finished.")
        
        return {"file_name": os.path.basename(file_path), "status": "generated & emailed"}
    
    except Exception as e:
        print(f"🔥 Task failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}

@celery_app.task
def cleanup_old_reports():
    threshold_days = 20
    folder = "generated_reports"
    now = datetime.now()

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - modified_time).days > threshold_days:
                os.remove(file_path)
                print(f"[CLEANUP] Deleted old report: {filename}")


# Scheduled/configurable report task
@celery_app.task
def generate_configurable_report(report_config: Dict[str, Any]):
    filters = report_config.get("filters") or {}

    if report_config.get("scheduled"):
        today = datetime.today().date()
        last_sunday = today - timedelta(days=today.weekday() + 1)
        last_monday = last_sunday - timedelta(days=6)
        filters["start_date"] = str(last_monday)
        filters["end_date"] = str(last_sunday)

    # Now you can call the manual report function to reuse logic
    return generate_report(
        report_name=report_config["report_name"],
        format=report_config["format"],
        start_date=filters.get("start_date"),
        end_date=filters.get("end_date")
    )

