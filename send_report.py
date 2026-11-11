import argparse
from contextlib import closing
from email.message import EmailMessage
import os
from pathlib import Path
import smtplib
import ssl

from report import DEFAULT_CSV, build_report


def build_message(csv_path: Path, sender: str, recipient: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = "Weekly Book Report"
    message.set_content(build_report(csv_path))
    message.add_attachment(
        csv_path.read_bytes(), maintype="text", subtype="csv", filename=csv_path.name
    )
    return message


def main():
    parser = argparse.ArgumentParser(description="Send a weekly book report through Gmail.")
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--to", help="Recipient address (defaults to the sender)")
    parser.add_argument("--port", type=int, choices=(587, 465), default=587,
                        help="Gmail SMTP port (587 for STARTTLS, 465 for implicit TLS)")
    args = parser.parse_args()

    sender = os.environ.get("GMAIL_ADDRESS", "").strip()
    password = "".join(os.environ.get("GMAIL_APP_PASSWORD", "").split())
    if not sender or not password:
        parser.error("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD before sending.")

    recipient = args.to or sender
    stage = "building the message"
    try:
        message = build_message(args.csv_path, sender, recipient)
        context = ssl.create_default_context()
        stage = f"connecting to Gmail on port {args.port}"
        if args.port == 465:
            connection = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30, context=context)
        else:
            connection = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)

        with closing(connection) as smtp:
            if args.port == 587:
                stage = "starting TLS"
                smtp.starttls(context=context)
            stage = "signing in to Gmail"
            smtp.login(sender, password)
            stage = "submitting the message to Gmail"
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError:
        parser.exit(1, "Gmail rejected the sign-in. Check the address and App Password.\n")
    except (OSError, ValueError, smtplib.SMTPException) as error:
        parser.exit(1, f"Email error while {stage}: {error}\n")

    print(f"Gmail accepted the report for {recipient}.")


if __name__ == "__main__":
    main()
