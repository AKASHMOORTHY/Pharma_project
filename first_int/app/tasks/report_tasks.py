from app.tasks.celery_utils import celery_app
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
from app.models.dashboard_models import DashboardProductionBatch, QualityCheck, Anomaly
from app.models.production_models import ProductionBatch
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import joinedload

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
def generate_report(report_name: str, format: str, start_date: str = None, end_date: str = None, shift: str = None):
    try:
        shift_str = f"_shift_{shift}" if shift else ""
        print(f"🔧 Generating report: {report_name}, {format}, shift={shift_str}")  


        db = SessionLocal()
        try:
            
            # Use dashboard tables as primary source for consistent data
            # Fetch dashboard production data
            dashboard_query = db.query(DashboardProductionBatch)
            if start_date:
                dashboard_query = dashboard_query.filter(DashboardProductionBatch.production_date >= start_date)
            if end_date:
                dashboard_query = dashboard_query.filter(DashboardProductionBatch.production_date <= end_date)
            if shift:
                dashboard_query = dashboard_query.filter(DashboardProductionBatch.shift == shift)
            
            dashboard_production = dashboard_query.all()
            
            # Fetch dashboard QC quality checks
            qc_query = db.query(QualityCheck)
            if start_date:
                qc_query = qc_query.filter(QualityCheck.created_at >= start_date)
            if end_date:
                qc_query = qc_query.filter(QualityCheck.created_at <= end_date)
            # if shift:
            #     qc_query = qc_query.filter(QualityCheck.shift == shift)
            qc_checks = qc_query.all()
            
            # Fetch detailed production batches for additional info (if needed)
            production_query = db.query(ProductionBatch).options(
                joinedload(ProductionBatch.stage_logs),
                joinedload(ProductionBatch.operator),
                joinedload(ProductionBatch.qc_tests)
            )
            
            if start_date:
                production_query = production_query.filter(ProductionBatch.date >= start_date)
            if end_date:
                production_query = production_query.filter(ProductionBatch.date <= end_date)
            if shift:
                production_query = production_query.filter(ProductionBatch.shift == shift)
            
            production_batches = production_query.all()
            
            # Create mapping between production batches and dashboard QC data
            # Group QC checks by date for matching with production data
            qc_by_date = {}
            for qc in qc_checks:
                qc_date = qc.created_at.strftime("%Y-%m-%d")
                if qc_date not in qc_by_date:
                    qc_by_date[qc_date] = []
                qc_by_date[qc_date].append(qc)
            
            # Process dashboard production data and separate by completion status
            complete_batches = []
            incomplete_batches = []
            anomaly_batches = []
            
            # Create lookup for detailed batch info
            production_lookup = {batch.id: batch for batch in production_batches}
            
            for dash_batch in dashboard_production:
                dash_date = dash_batch.production_date.strftime("%Y-%m-%d")
                
                # Get corresponding detailed production batch if available
                detailed_batch = production_lookup.get(dash_batch.id)
                
                # Get QC information for this date
                qc_for_date = qc_by_date.get(dash_date, [])
                qc_result = "Not Tested"
                
                if qc_for_date:
                    # Use the most recent QC result for this date
                    latest_qc = max(qc_for_date, key=lambda x: x.created_at)
                    qc_result = latest_qc.result  # "Pass" or "Fail"
                
                # Get stage completion status from detailed batch
                
                completed_stages = "0/0"
                operator_name = "N/A"
                incomplete_stage_flag = False

                
                if detailed_batch:
                    completed_stage_count = sum(1 for log in detailed_batch.stage_logs if log.status == "Completed")
                    total_stage_count = len(detailed_batch.stage_logs)
                    completed_stages = f"{completed_stage_count}/{total_stage_count}"
                    operator_name = detailed_batch.operator.full_name if detailed_batch.operator else "N/A"
                    incomplete_stage_flag = completed_stage_count < total_stage_count
                
                # Use dashboard status as primary indicator
                is_completed_status = dash_batch.status == "Completed"
                
                batch_data = {
                    "batch_id": dash_batch.id,
                    "date": dash_date,
                    "shift": dash_batch.shift,
                    "status": dash_batch.status,
                    "duration": f"{dash_batch.duration:.2f}h" if dash_batch.duration else "N/A",
                    "completed_stages": completed_stages,
                    "qc_result": qc_result,
                    "operator": operator_name
                }
                
                # Separate complete vs incomplete based on dashboard status and QC
                if is_completed_status and qc_result in ["Pass", "Fail"]:
                    complete_batches.append(batch_data)
                else:
                    incomplete_batches.append(batch_data)

                # Anomaly: QC Fail or incomplete stages
                if qc_result == "Fail" or incomplete_stage_flag:
                    anomaly_batches.append(batch_data)
            # Dashboard summary using the production data
            dashboard_summary = []
            for dash_batch in dashboard_production:
                dashboard_summary.append({
                    "date": dash_batch.production_date.strftime("%Y-%m-%d"),
                    "shift": dash_batch.shift,
                    "status": dash_batch.status,
                    "duration": f"{dash_batch.duration:.2f}h" if dash_batch.duration else "N/A",
                })
            
            # Prepare structured data for report
            data = {
                "complete_batches": complete_batches,
                "incomplete_batches": incomplete_batches,
                "anomaly_batches": anomaly_batches,
                "dashboard_summary": dashboard_summary,
                "qc_summary": {
                    "total_qc_checks": len(qc_checks),
                    "passed_qc": len([qc for qc in qc_checks if qc.result == "Pass"]),
                    "failed_qc": len([qc for qc in qc_checks if qc.result == "Fail"]),
                },
                "report_generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        finally:
            db.close()

        # Standardize format to lowercase
        format = format.lower()
        file_id = f"{report_name}{shift_str}_{uuid.uuid4().hex[:6]}"
        file_path = f"generated_reports/{file_id}.{format}"

        print("📁 Writing file:", file_path)
        # Save as CSV or PDF
        if format == "csv":
            with open(file_path, mode="w", newline="") as f:
                # Write complete batches
                if data["complete_batches"]:
                    f.write("COMPLETE BATCHES\n")
                    writer = csv.DictWriter(f, fieldnames=data["complete_batches"][0].keys())
                    writer.writeheader()
                    writer.writerows(data["complete_batches"])
                    f.write("\n")
                
                # Write incomplete batches
                if data["incomplete_batches"]:
                    f.write("INCOMPLETE BATCHES\n")
                    writer = csv.DictWriter(f, fieldnames=data["incomplete_batches"][0].keys())
                    writer.writeheader()
                    writer.writerows(data["incomplete_batches"])
                    f.write("\n")
                
                if data["anomaly_batches"]:
                    f.write("ANOMALY BATCHES\n")
                    writer = csv.DictWriter(f, fieldnames=data["anomaly_batches"][0].keys())
                    writer.writeheader()
                    writer.writerows(data["anomaly_batches"])
                    f.write("\n")

                # Write QC summary
                f.write("QC SUMMARY\n")
                for key, value in data["qc_summary"].items():
                    f.write(f"{key},{value}\n")

        elif format == "pdf":
            html_template = """
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { border: 1px solid black; border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                    th, td { border: 1px solid black; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; font-weight: bold; }
                    h1 { color: #333; text-align: center; }
                    h2 { color: #666; border-bottom: 2px solid #ccc; padding-bottom: 5px; }
                    h3 { color: #888; }
                    .summary-box { background-color: #f9f9f9; padding: 15px; border: 1px solid #ddd; margin-bottom: 20px; }
                    .status-pass { color: green; font-weight: bold; }
                    .status-fail { color: red; font-weight: bold; }
                    .status-pending { color: orange; font-weight: bold; }
                    .header-info { text-align: center; margin-bottom: 30px; }
                </style>
            </head>
            <body>
                <div class="header-info">
                    <h1>{{ title }}</h1>
                    <p><strong>Report Generated:</strong> {{ data.report_generated_at }}</p>
                </div>

                <!-- Summary -->
                <div class="summary-box">
                    <h3>Quality Control Summary</h3>
                    <p><strong>Total QC Checks:</strong> {{ data.qc_summary.total_qc_checks }}</p>
                    <p><strong>Passed QC:</strong> <span class="status-pass">{{ data.qc_summary.passed_qc }}</span></p>
                    <p><strong>Failed QC:</strong> <span class="status-fail">{{ data.qc_summary.failed_qc }}</span></p>
                </div>

                <!-- Complete Batches -->
                <h2>✅ Complete Batches ({{ data.complete_batches|length }})</h2>
                {% if data.complete_batches %}
                <table>
                    <tr>
                        <th>Batch ID</th>
                        <th>Date</th>
                        <th>Shift</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>QC Result</th>
                        <th>Operator</th>
                    </tr>
                    {% for batch in data.complete_batches %}
                    <tr>
                        <td>{{ batch.batch_id }}</td>
                        <td>{{ batch.date }}</td>
                        <td>{{ batch.shift }}</td>
                        <td>{{ batch.status }}</td>
                        <td>{{ batch.duration }}</td>
                        <td class="{% if batch.qc_result == 'Pass' %}status-pass{% elif batch.qc_result == 'Fail' %}status-fail{% else %}status-pending{% endif %}">
                            {{ batch.qc_result }}
                        </td>
                        <td>{{ batch.operator }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <p><em>No complete batches found for the specified period.</em></p>
                {% endif %}

                <!-- Incomplete Batches -->
                <h2>⏳ Incomplete Batches ({{ data.incomplete_batches|length }})</h2>
                {% if data.incomplete_batches %}
                <table>
                    <tr>
                        <th>Batch ID</th>
                        <th>Date</th>
                        <th>Shift</th>
                        <th>Status</th>
                        <th>Duration</th>                    
                        <th>QC Result</th>
                        <th>Operator</th>
                    </tr>
                    {% for batch in data.incomplete_batches %}
                    <tr>
                        <td>{{ batch.batch_id }}</td>
                        <td>{{ batch.date }}</td>
                        <td>{{ batch.shift }}</td>
                        <td>{{ batch.status }}</td>
                        <td>{{ batch.duration }}</td>
                        <td class="{% if batch.qc_result == 'Pass' %}status-pass{% elif batch.qc_result == 'Fail' %}status-fail{% else %}status-pending{% endif %}">
                            {{ batch.qc_result }}
                        </td>
                        <td>{{ batch.operator }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <p><em>No incomplete batches found for the specified period.</em></p>
                {% endif %}

                <!-- Anomaly Batches -->
                <h2>🚨 Anomaly Batches ({{ data.anomaly_batches|length }})</h2>
                {% if data.anomaly_batches %}
                <table>
                    <tr>
                        <th>Batch ID</th>
                        <th>Date</th>
                        <th>Shift</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>QC Result</th>
                        <th>Operator</th>
                    </tr>
                    {% for batch in data.anomaly_batches %}
                    <tr>
                        <td>{{ batch.batch_id }}</td>
                        <td>{{ batch.date }}</td>
                        <td>{{ batch.shift }}</td>
                        <td>{{ batch.status }}</td>
                        <td>{{ batch.duration }}</td>
                        <td class="{% if batch.qc_result == 'Pass' %}status-pass{% elif batch.qc_result == 'Fail' %}status-fail{% else %}status-pending{% endif %}">
                            {{ batch.qc_result }}
                        </td>
                        <td>{{ batch.operator }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% else %}
                <p><em>No anomaly batches found for the specified period.</em></p>
                {% endif %}

                <!-- Dashboard Summary (if available) -->
                {% if data.dashboard_summary %}
                <h2>📊 Dashboard Summary</h2>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Shift</th>
                        <th>Status</th>
                        <th>Duration</th>
                    </tr>
                    {% for item in data.dashboard_summary %}
                    <tr>
                        <td>{{ item.date }}</td>
                        <td>{{ item.shift }}</td>
                        <td>{{ item.status }}</td>
                        <td>{{ item.duration }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </body>
            </html>
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
    threshold_days = 30
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
        filters["shift"] = "All"

    # Now you can call the manual report function to reuse logic
    return generate_report(
        report_name=report_config["report_name"],
        format=report_config["format"],
        start_date=filters.get("start_date"),
        end_date=filters.get("end_date"),
        shift=filters.get("shift")
    )

@celery_app.task
def generate_anomaly_report():
    db = SessionLocal()
    try:
        anomalies = db.query(Anomaly).filter(Anomaly.resolved_at == None).all()
        reports_dir = os.path.join(os.getcwd(), "generated_reports")
        os.makedirs(reports_dir, exist_ok=True)
        file_id = f"Anomaly_{uuid.uuid4().hex[:6]}"
        pdf_path = f"generated_reports/{file_id}.pdf"
        

        if not anomalies:
            print("✅ No anomalies found.")
            return "No anomalies found."

        print(f"🔍 Total anomalies: {len(anomalies)}")
        # Generate PDF report
        html = "<h1>Anomaly Report</h1>"
        for anomaly in anomalies:
            html += f"""
            <div style='margin-bottom:20px;'>
                <b>Anomaly ID:</b> {anomaly.id}<br>
                <b>Status:</b> {anomaly.status}<br>
                <b>Created At:</b> {anomaly.created_at.strftime('%Y-%m-%d %H:%M:%S')}<br>
                <b>Resolved At:</b> {anomaly.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if anomaly.resolved_at else 'Not resolved'}<br>
            </div>
            """
        with open(pdf_path, "wb") as f:
            pisa.CreatePDF(html, dest=f)

        
        print(f"📄 PDF report generated at {pdf_path}")

        # send_email_alert.delay(
        #     subject="📝 Detailed Anomaly Report",
        #     message="Please find the attached anomaly report PDF.",
        #     attachments=[pdf_path]
        # )
        print("📤 Sending email to:", EMAIL_TO)
        try:
            if not os.path.isfile(pdf_path):
                print(f"[EMAIL FAILED] Report file not found: {pdf_path}")
                return {"status": "failed", "reason": f"Report file not found: {pdf_path}"}

            email = EmailMessage()
            email['Subject'] = "Anomaly Report Generation"
            email['From'] = EMAIL_USER
            email['To'] = EMAIL_TO
            email.set_content("Please find the attached anomaly report PDF.")

            # Attach files
            with open(pdf_path, 'rb') as f:
                file_data = f.read()
                file_name = file_id + ".pdf"
            email.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_USER, EMAIL_PASS)
                smtp.send_message(email)

            print(f"[EMAIL SENT] Anomaly report sent to {EMAIL_TO}")
        except Exception as e:
            print(f"[EMAIL FAILED] Error sending email: {str(e)}")
  
        print("✅ Task finished.")
        
        return {"file_name": os.path.basename(pdf_path), "status": "Anomaly report generated & emailed"}


    except Exception as e:
        print(f"❌ Error generating anomaly report: {e}")
        db.rollback()
        return ""
    finally:
        db.close()
