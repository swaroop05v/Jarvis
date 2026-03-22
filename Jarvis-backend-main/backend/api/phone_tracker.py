import subprocess
import csv
import os
import time
import requests
from datetime import datetime, date
import pandas as pd

LOG_FILE = os.path.join(os.path.dirname(__file__), "activity_log.csv")
ADB = r"C:\Users\swaroop\Downloads\platform-tools\adb.exe"
API_URL = "http://localhost:5000"

PACKAGE_NAMES = {
    "com.google.android.youtube": "YouTube",
    "com.instagram.android": "Instagram",
    "com.whatsapp": "WhatsApp",
    "com.netflix.mediaclient": "Netflix",
    "com.twitter.android": "Twitter",
    "com.facebook.katana": "Facebook",
    "com.tiktok.android": "TikTok",
    "com.google.android.gm": "Gmail",
    "com.google.android.apps.maps": "Google Maps",
    "com.spotify.music": "Spotify",
    "com.google.android.apps.docs": "Google Docs",
    "com.microsoft.office.word": "Word",
    "com.google.android.chrome": "Chrome (Mobile)",
    "com.samsung.android.browser": "Samsung Browser",
    "com.android.settings": "Settings",
    "com.android.launcher3": "Home Screen",
    "com.oneplus.launcher": "Home Screen",
    "com.coloros.launcher": "Home Screen",
    "com.oppo.launcher": "Home Screen",
    "com.google.android.apps.messaging": "Messages",
    "com.google.android.dialer": "Phone",
    "com.google.android.apps.photos": "Photos",
    "com.snapchat.android": "Snapchat",
    "com.reddit.frontpage": "Reddit",
    "com.linkedin.android": "LinkedIn",
    "com.amazon.mShop.android.shopping": "Amazon",
    "com.discord": "Discord",
    "com.supercell.clashofclans": "Clash of Clans",
    "com.application.zomato": "Zomato",
    "com.rapido.passenger": "Rapido",
    "com.microsoft.office.outlook": "Outlook",
}

SKIP_PACKAGES = {
    "com.android.systemui",
    "com.android.launcher",
    "com.android.launcher3",
    "com.coloros.launcher",
    "com.oppo.launcher",
    "com.oneplus.launcher",
    "com.miui.home",
    "null",
    "",
}

DISTRACTING_APPS = [
    "YouTube", "Instagram", "Netflix", "Twitter",
    "TikTok", "Facebook", "WhatsApp", "Snapchat", "Reddit"
]

notified_milestones = {}  # app -> last notified minute bucket
NOTIFY_EVERY_MINS = 10


def send_phone_notification(title: str, message: str):
    try:
        adb_cmd = [
    ADB, "shell", "cmd", "notification", "post",
    "-S", "bigtext",
    "-t", title,
    "-T", message,
    "JarvisWellness",
    message
]
        subprocess.run(adb_cmd, capture_output=True, timeout=5)
        print(f"[phone_tracker] Notification sent: {title} — {message}")
    except Exception as e:
        print(f"[phone_tracker] Notification error: {e}")


def get_wellness_score() -> int:
    try:
        res = requests.get(f"{API_URL}/api/wellness", timeout=3)
        data = res.json()
        return data.get("wellness_score", 100)
    except:
        return 100


def check_and_notify(app_name: str, wellness_score: int):
    """Fire notification every 10 mins of distracting app usage."""
    is_distracting = any(d.lower() in app_name.lower() for d in DISTRACTING_APPS)
    if not is_distracting:
        return

    try:
        df = pd.read_csv(LOG_FILE, encoding='utf-8', encoding_errors='ignore',
                         usecols=['timestamp', 'app', 'duration_seconds'])
        df["timestamp"] = pd.to_datetime(df["timestamp"], format='mixed')
        today_rows = df[
            (df["timestamp"].dt.date == date.today()) &
            (df["app"] == app_name)
        ]
        usage_mins = (len(today_rows) * 5) // 60
    except:
        return

    if usage_mins == 0:
        return

    # Which 10-min bucket are we in?
    current_bucket = (usage_mins // NOTIFY_EVERY_MINS) * NOTIFY_EVERY_MINS
    if current_bucket == 0:
        return

    last_bucket = notified_milestones.get(app_name, 0)
    if current_bucket <= last_bucket:
        return

    # Fire notification
    notified_milestones[app_name] = current_bucket
    clean_name = app_name.replace("[Phone] ", "")

    if current_bucket <= 20:
        tone = "Still okay, but stay aware."
    elif current_bucket <= 40:
        tone = f"Wellness at {wellness_score}/100 — consider a break."
    else:
        tone = f"Wellness dropping to {wellness_score}/100. Put it down."

    send_phone_notification(
        "Jarvis Wellness ⚡",
        f"Take a break! {current_bucket} mins on {clean_name}. {tone}"
    )


def check_adb_connected() -> bool:
    try:
        result = subprocess.run(
            [ADB, "devices"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().splitlines()
        devices = [l for l in lines[1:] if l.strip().endswith("device")]
        return len(devices) > 0
    except Exception:
        return False


def get_foreground_app():
    try:
        result = subprocess.run(
            [ADB, "shell", "dumpsys", "window"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "mCurrentFocus" in line and " u0 " in line:
                after_u0 = line.split(" u0 ")[1]
                package = after_u0.split("/")[0].strip()

                if package in SKIP_PACKAGES:
                    return None
                if any(x in package.lower() for x in ["notification", "shade", "systemui", "launcher"]):
                    return None

                friendly = PACKAGE_NAMES.get(package, None)
                if friendly:
                    return f"[Phone] {friendly}"
                short = package.split(".")[-1].capitalize()
                return f"[Phone] {short}"

        for line in result.stdout.splitlines():
            if "mFocusedApp" in line and " u0 " in line:
                after_u0 = line.split(" u0 ")[1]
                package = after_u0.split("/")[0].strip()

                if package in SKIP_PACKAGES:
                    return None
                if any(x in package.lower() for x in ["notification", "shade", "systemui", "launcher"]):
                    return None

                friendly = PACKAGE_NAMES.get(package, None)
                if friendly:
                    return f"[Phone] {friendly}"
                short = package.split(".")[-1].capitalize()
                return f"[Phone] {short}"

    except Exception as e:
        print(f"[phone_tracker] ADB error: {e}")
    return None


def ensure_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "app", "duration_seconds"])
        print(f"[phone_tracker] Created log file: {LOG_FILE}")


def run_phone_tracker():
    ensure_log()

    print("[phone_tracker] Checking ADB connection...")
    if not check_adb_connected():
        print("[phone_tracker] No device found. Make sure USB debugging is on and phone is connected.")
        return

    print("[phone_tracker] Device connected. Starting...")
    print(f"[phone_tracker] Logging to: {LOG_FILE}")
    print("[phone_tracker] Wellness notifications active — fires every 10 mins on distracting apps.")
    print("[phone_tracker] Press Ctrl+C to stop.\n")

    loop_count = 0

    while True:
        app = get_foreground_app()

        if app:
            timestamp = datetime.now().isoformat()

            with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, app, 5])

            # Check notifications every 12 loops (~60 seconds)
            if loop_count % 12 == 0:
                wellness = get_wellness_score()
                check_and_notify(app, wellness)

            try:
                df = pd.read_csv(LOG_FILE, encoding='utf-8', encoding_errors='ignore',
                                 usecols=['timestamp', 'app', 'duration_seconds'])
                df["timestamp"] = pd.to_datetime(df["timestamp"], format='mixed')
                today_phone = df[
                    (df["timestamp"].dt.date == date.today()) &
                    (df["app"].str.startswith("[Phone]", na=False))
                ]
                total_secs = len(today_phone) * 5
                mins = total_secs // 60
                secs = total_secs % 60
                print(f"{timestamp} | {app} | Phone today: {mins}m {secs}s")
            except:
                print(f"{timestamp} | {app}")

        loop_count += 1
        time.sleep(5)


if __name__ == "__main__":
    run_phone_tracker()