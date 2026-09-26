# price-texts

An hourly text message with TQQQ and Bitcoin prices, sent to my phone from 8am to 10pm ET. It's built for people who check their texts but forget to check a widget.

```
/ 10:55pm / TQQQ $78.05 (closed)
-0.8% today

BTC $84,228
-0.1% 24h | -0.4% 1h
```

It costs nothing to run: no server, no texting service, no paid API.

## How it works

1. A GitHub Actions schedule tries to run `prices.py` four times an hour (:08, :23, :38, :53). GitHub drops many scheduled runs, so the extra tries raise the odds that at least one gets through. The first run each ET hour sends and saves a marker in the Actions cache, and later runs that hour see the marker and skip. The minutes are the cron lines in `.github/workflows/hourly.yml`.
2. The script pulls prices from Yahoo Finance, including TQQQ pre-market and after-hours. It works out the change for the day (24 hours for BTC) and for the last hour.
3. It emails the message through Gmail to T-Mobile's email-to-text address (`<number>@tmomail.net`), and it arrives as a regular SMS.

A few things about T-Mobile's gateway:
- It shows the email subject as `/ subject /` at the start of every text, so the subject holds the time.
- It strips emoji and other non-plain characters, so the message sticks to plain text.

## Set it up for yourself

1. Fork this repo.
2. Create a [Gmail app password](https://myaccount.google.com/apppasswords). This needs 2-Step Verification turned on.
3. Add three repository secrets under Settings > Secrets and variables > Actions:
   - `GMAIL_USER`: your Gmail address
   - `GMAIL_APP_PASSWORD`: the 16-letter app password
   - `SMS_TO`: your number at your carrier's gateway, like `5551234567@tmomail.net`
4. Go to Actions > Hourly price text > Run workflow to send a test.

To try it locally without sending anything, run `python3 prices.py --force --dry-run`.

To change the tickers or the hours, edit `prices.py`. The waking hours are `WAKE_START` and `WAKE_END`.

## Notes

- Not every carrier has a gateway: AT&T shut its email-to-text gateway down in 2025. T-Mobile works, and Verizon (`vtext.com`) mostly does.
- GitHub's schedule is best effort. On 25-26 Sep 2026 a once-an-hour cron fired only about every 4-5 hours, which is why it now tries four times an hour. If hours still go missing, the reliable fix is an outside timer (like a Cloudflare Worker cron) that triggers the workflow with Run workflow through the API.
- T-Mobile's gateway can hold a text for hours: one sent at 7:14pm arrived at 10:28pm. The time in the subject is when it was sent.
- GitHub pauses schedules on public repos after 60 days with no activity. A weekly keepalive workflow prevents that.
