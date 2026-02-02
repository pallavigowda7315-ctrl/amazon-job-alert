import time
import smtplib
import requests
import os
import requests

from email.mime.text import MIMEText

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================
# CONFIG
# ==========================
URL = "https://www.jobsatamazon.co.uk/app#/jobSearch"
CHECK_INTERVAL = 60  # seconds

# ---- EMAIL ----
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_SENDER = "pallavigowda7315@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVERS = [
    "pallavigowda7315@gmail.com",
    "nayakakiran31@gmail.com"
]

# ---- TELEGRAM ----

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_ID").split(",")

# ==========================
# ALERT FUNCTIONS
# ==========================
def send_email_alert():
    msg = MIMEText(
        "🚨 Amazon jobs are now AVAILABLE!\n\n"
        "- Location: LE3 5\n"
        "- Part time\n"
        "- Within 30 miles\n\n"
        f"Apply now:\n{URL}"
    )
    msg["Subject"] = "🚀 Amazon Job Alert (LE3 5)"
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECEIVERS)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVERS, msg.as_string())

# def send_telegram_alert():
#     message = (
#         "🚨 *AMAZON JOBS AVAILABLE!*\n\n"
#         "📍 Location: LE3 5\n"
#         "🕒 Part time\n"
#         "📏 Within 30 miles\n\n"
#         f"👉 Apply now:\n{URL}"
#     )

#     requests.post(
#         f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
#         data={
#             "chat_id": CHAT_ID,
#             "text": message,
#             "parse_mode": "Markdown"
#         }
#     )

def send_telegram_alert():
    message = (
        "🚨 *AMAZON JOBS AVAILABLE!*\n\n"
        "📍 Location: LE3 5\n"
        "🕒 Part time\n"
        "📏 Within 30 miles\n\n"
        f"👉 Apply now:\n{URL}"
    )

    for chat_id in CHAT_IDS:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": chat_id.strip(),
                "text": message,
                "parse_mode": "Markdown"
            }
        )
# ==========================
# SELENIUM SETUP
# ==========================
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 20)
driver.get(URL)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

print("🔍 Monitoring Amazon Jobs (EMAIL + TELEGRAM enabled)...")

# ==========================
# JOB CHECK LOGIC
# ==========================
def jobs_available():
    no_jobs = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'Sorry, there are no jobs available')]"
    )
    job_cards = driver.find_elements(
        By.CSS_SELECTOR,
        "a[data-testid='job-card'], div.job-card"
    )
    return len(job_cards) > 0 and len(no_jobs) == 0

# ==========================
# MAIN LOOP
# ==========================
alert_sent = False

while not alert_sent:
    time.sleep(8)

    if jobs_available():
        print("🎉 REAL JOBS FOUND!")
        send_email_alert()
        send_telegram_alert()
        print("📧 Email + 📱 Telegram alerts sent!")
        alert_sent = True
        break
    else:
        print("⏳ No jobs yet. Checking again...")

    time.sleep(CHECK_INTERVAL)
    driver.refresh()

driver.quit()
