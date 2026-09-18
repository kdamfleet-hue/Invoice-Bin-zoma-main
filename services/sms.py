"""SMS provider boundary for authentication OTP messages.

Sending is disabled unless explicitly configured in the deployment environment.
No OTP code or provider secret is ever logged here.
"""
import os

import requests


def send_login_otp_sms(phone, code):
    provider = (os.environ.get("SMS_PROVIDER") or "disabled").strip().lower()
    if provider == "disabled":
        raise RuntimeError("SMS provider is not configured")
    if provider != "generic_http":
        raise RuntimeError("Unsupported SMS provider")

    response = requests.post(
        os.environ["SMS_API_URL"],
        headers={
            "Authorization": f"Bearer {os.environ['SMS_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "to": phone,
            "message": f"رمز الدخول إلى BIN ZOMAH INTL هو: {code}. صالح لمدة 5 دقائق.",
            "sender": os.environ.get("SMS_SENDER_ID", "BINZOMAH"),
        },
        timeout=10,
    )
    response.raise_for_status()
    return True
