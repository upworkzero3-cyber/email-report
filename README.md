# Weekly Book Report

Generate a plain-text summary of a books CSV and email it through Gmail with the original CSV attached.

## Set up

Run these commands in PowerShell from the project directory.

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Preview the report

```powershell
.\venv\Scripts\python.exe .\report.py 'D:\web-scraper\output\books.csv'
```

The CSV needs `price` and `rating` columns. Prices can use a consistent leading currency symbol (£, $, or €). Ratings can be numbers or the words one through five. The report shows the total number of rows, average price, and average rating. If you omit the path, both scripts look for `web-scraper\output\books.csv` next to the project directory.

## Send a test email

Enable 2-Step Verification on a dedicated test Gmail account and create a [Google App Password](https://support.google.com/accounts/answer/185833). Run these commands in PowerShell. The script sends to the sender's inbox by default.

```powershell
$env:GMAIL_ADDRESS = Read-Host "Test Gmail address"
$appPassword = Read-Host "Google App Password" -AsSecureString
$env:GMAIL_APP_PASSWORD = [System.Net.NetworkCredential]::new("", $appPassword).Password

try {
    .\venv\Scripts\python.exe .\send_report.py 'D:\web-scraper\output\books.csv' --port 465
} finally {
    Remove-Item Env:\GMAIL_APP_PASSWORD
    Remove-Variable appPassword
}
```

Look for **Weekly Book Report** and its CSV attachment. Pass `--to recipient@example.com` to send to a different address. The default SMTP port is 587 with STARTTLS. Port 465 uses implicit TLS.

Keep the App Password private. The sender reads it from the current process environment. For scheduled runs, have the scheduler supply both environment variables securely.
