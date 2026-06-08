import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.core.config import settings


def send_email_alert(subject: str, body: str) -> bool:
    if not settings.EMAIL_ADDRESS or not settings.EMAIL_PASSWORD:
        print("Email not configured")
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL_ADDRESS
        msg["To"] = settings.ALERT_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_ADDRESS, settings.ALERT_EMAIL, msg.as_string())
        print(f"Email alert sent: {subject}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_slack_alert(message: str) -> bool:
    if not settings.SLACK_BOT_TOKEN or not settings.SLACK_CHANNEL:
        print("Slack not configured")
        return False
    try:
        client = WebClient(token=settings.SLACK_BOT_TOKEN)
        client.chat_postMessage(
            channel=settings.SLACK_CHANNEL,
            text=message,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🚨 *ThreatLens Alert*\n{message}"
                    }
                }
            ]
        )
        print("Slack alert sent")
        return True
    except SlackApiError as e:
        print(f"Slack error: {e}")
        return False


def send_critical_threat_alert(threat) -> dict:
    subject = f"🚨 CRITICAL THREAT DETECTED: {threat.value}"
    body = f"""
    <h2>Critical Threat Alert</h2>
    <p><strong>Indicator:</strong> {threat.value}</p>
    <p><strong>Type:</strong> {threat.type}</p>
    <p><strong>Risk Score:</strong> {threat.risk_score}/100</p>
    <p><strong>Source:</strong> {threat.source}</p>
    <p><strong>Tags:</strong> {threat.tags}</p>
    <p><strong>Description:</strong> {threat.description}</p>
    <hr>
    <p>Login to ThreatLens to investigate immediately.</p>
    """

    slack_msg = (
        f"🚨 CRITICAL: {threat.type.upper()} `{threat.value}` "
        f"| Risk Score: {threat.risk_score}/100 "
        f"| Source: {threat.source} "
        f"| Tags: {threat.tags}"
    )

    email_sent = send_email_alert(subject, body)
    slack_sent = send_slack_alert(slack_msg)

    return {
        "email_sent": email_sent,
        "slack_sent": slack_sent,
        "threat": threat.value,
    }