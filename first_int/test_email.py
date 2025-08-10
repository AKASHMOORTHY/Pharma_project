#!/usr/bin/env python3
"""
Test script to check email functionality
"""

import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv()

def test_email_sending():
    """Test email sending functionality"""
    EMAIL_SENDER = os.getenv("SMTP_USER")
    EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL_DEFAULT_RECEIVER = os.getenv("EMAIL_TO")

    print(f"Sender: {EMAIL_SENDER}")
    print(f"Receiver: {EMAIL_DEFAULT_RECEIVER}")
    print(f"Password set: {'Yes' if EMAIL_PASSWORD else 'No'}")

    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_DEFAULT_RECEIVER]):
        print("❌ Missing email configuration!")
        return False

    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_DEFAULT_RECEIVER
    msg["Subject"] = "🧪 Test Email from Pharma System"
    msg.set_content("This is a test email to verify email functionality is working properly.")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            print("🔗 Connecting to Gmail SMTP...")
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            print("✅ Login successful!")
            smtp.send_message(msg)
            print("✅ Email sent successfully!")
            return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Email Functionality")
    print("=" * 40)
    
    if test_email_sending():
        print("\n🎉 Email test passed! Check your inbox.")
    else:
        print("\n⚠️ Email test failed! Check the errors above.")

