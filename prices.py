"""Hourly TQQQ + BTC price text, sent to a T-Mobile phone via email-to-text."""
import json
import os
import smtplib
import sys
import urllib.request
from datetime import datetime
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
WAKE_START, WAKE_END = 8, 22  # texts go out 8am to 10pm ET


def chart(symbol):
    # 5-min bars over 2 days, incl. pre/post market, so we can look back an hour
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           "?interval=5m&range=2d&includePrePost=true")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["chart"]["result"][0]


def pct(now, then):
    return f"{(now - then) / then * 100:+.1f}%"


def quote(symbol):
    res = chart(symbol)
    closes = res["indicators"]["quote"][0]["close"]
    bars = [(t, c) for t, c in zip(res["timestamp"], closes) if c is not None]
    t_now, price = bars[-1]

    def ago(secs):
        return next((c for t, c in reversed(bars) if t <= t_now - secs), bars[0][1])

    return price, ago, res["meta"], t_now


def session(meta, t):
    p = meta.get("currentTradingPeriod", {})
    for name, key in (("pre", "pre"), ("", "regular"), ("after", "post")):
        if p.get(key) and p[key]["start"] <= t < p[key]["end"]:
            return name
    return "closed"


def dot(now, then):
    return "🟢" if now >= then else "🔴"


def build():
    now = datetime.now(ET)

    price, ago, meta, t = quote("TQQQ")
    tag = session(meta, t) if now.timestamp() - t < 1800 else "closed"
    # pre-market compares to yesterday's close; otherwise to the prior session's close
    base = meta["regularMarketPrice"] if tag == "pre" else meta["previousClose"]
    detail = [f"{pct(price, base)} today"]
    if tag != "closed":
        detail.append(f"{pct(price, ago(3600))} 1h")
    if tag:
        detail.append(tag)
    tqqq = f"📈 TQQQ  ${price:,.2f}\n{dot(price, base)} {' · '.join(detail)}"

    price, ago, _, _ = quote("BTC-USD")
    day = ago(86400)
    btc = f"🪙 BTC  ${price:,.0f}\n{dot(price, day)} {pct(price, day)} 24h · {pct(price, ago(3600))} 1h"

    return f"{tqqq}\n\n{btc}\n\n{now.strftime('%-I:%M%p').lower()}"


def send(body):
    user, pw, to = os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"], os.environ["SMS_TO"]
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"], msg["To"] = user, to  # no Subject, T-Mobile shows it as "/ /"
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pw)
        s.sendmail(user, [to], msg.as_string())


if __name__ == "__main__":
    force = "--force" in sys.argv
    hour = datetime.now(ET).hour
    if not force and not (WAKE_START <= hour < WAKE_END):
        print(f"{hour}:00 ET is outside waking hours, skipping")
        sys.exit(0)
    body = build()
    print(body)
    if "--dry-run" not in sys.argv:
        send(body)
