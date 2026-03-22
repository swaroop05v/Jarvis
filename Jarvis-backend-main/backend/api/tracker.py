"""
tracker.py — PC activity tracker.

Writes source='pc' to activity_log.csv.
FIX: Now detects system idle and skips logging when:
  - User has been idle for more than IDLE_THRESHOLD_SECONDS (default 60s)
  - This prevents sleep/screensaver time from inflating screen time

Run both trackers simultaneously in separate terminals:
    python tracker.py        # terminal 1 — PC tracking
    python phone_tracker.py  # terminal 2 — phone tracking (requires ADB)
"""

import time
import csv
import os
import ctypes
import ctypes.wintypes
import pandas as pd
from datetime import datetime, timedelta

LOG_FILE = os.path.join(os.path.dirname(__file__), "activity_log.csv")

KEEP_DAYS = 7

# If the user hasn't moved mouse or pressed a key for this many seconds,
# skip logging — they're idle, sleeping, or stepped away.
IDLE_THRESHOLD_SECONDS = 60


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.wintypes.UINT),
        ('dwTime', ctypes.wintypes.DWORD)
    ]


def get_idle_seconds() -> float:
    """
    Returns how many seconds since the user last moved the mouse or
    pressed a key on Windows, using GetLastInputInfo.
    Returns 0 on non-Windows platforms (fallback — always log).
    """
    try:
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return millis / 1000.0
    except Exception:
        return 0.0  # non-Windows: always log


def is_user_active() -> bool:
    """Return True if the user has been active within the last IDLE_THRESHOLD_SECONDS."""
    return get_idle_seconds() < IDLE_THRESHOLD_SECONDS


def trim_log():
    """Remove entries older than KEEP_DAYS from the log file."""
    if not os.path.exists(LOG_FILE):
        return
    try:
        df = pd.read_csv(LOG_FILE, encoding='utf-8', encoding_errors='ignore')
        if df.empty:
            return
        df["timestamp"] = pd.to_datetime(df["timestamp"], format='mixed')
        cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
        before = len(df)
        df = df[df["timestamp"] >= cutoff]
        after = len(df)
        df.to_csv(LOG_FILE, index=False, encoding='utf-8')
        if before != after:
            print(f"Trimmed {before - after} old entries (keeping last {KEEP_DAYS} days)")
    except Exception as e:
        print(f"Warning: could not trim log: {e}")


def get_active_window():
    try:
        import pygetwindow as gw
        win = gw.getActiveWindow()
        if win and win.title:
            safe_title = win.title.encode('ascii', errors='replace').decode('ascii')
            return safe_title
        return "Unknown"
    except Exception:
        return "Unknown"


def ensure_log_headers():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "app", "duration_seconds", "source"])
        print(f"Created log file: {LOG_FILE}")


def log_activity():
    ensure_log_headers()
    trim_log()

    print(f"PC Tracker running... keeping last {KEEP_DAYS} days of data.")
    print(f"Idle threshold: {IDLE_THRESHOLD_SECONDS}s — skips logging when idle/sleeping.")
    print(f"Logging to: {LOG_FILE}")
    print("Press Ctrl+C to stop.")

    entry_count = 0
    idle_skips = 0

    while True:
        # FIX: Skip logging if user is idle — prevents sleep/screensaver
        # time from inflating screen time figures.
        if not is_user_active():
            idle_seconds = get_idle_seconds()
            idle_skips += 1
            if idle_skips % 12 == 1:  # print every ~60s of idling
                print(f"[idle {idle_seconds:.0f}s — not logging]")
            time.sleep(5)
            continue

        idle_skips = 0  # reset when active again
        app = get_active_window()
        timestamp = datetime.now().isoformat()

        with open(LOG_FILE, "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, app, 5, "pc"])

        print(f"{timestamp} | [pc] {app}")

        entry_count += 1
        if entry_count % 17280 == 0:
            trim_log()

        time.sleep(5)


if __name__ == "__main__":
    log_activity()
