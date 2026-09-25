# price-texts

Hourly text with TQQQ and BTC-USD prices, 8am to 10pm ET. Runs on GitHub Actions, sends through Gmail to the T-Mobile email-to-text gateway (`<number>@tmomail.net`).

Secrets: `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `SMS_TO`.

Test locally without sending: `python3 prices.py --force --dry-run`. Send one now: Actions tab, "Hourly price text", Run workflow.
