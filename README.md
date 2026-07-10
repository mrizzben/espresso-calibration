# Espresso Calibration

> "I'm too tired to keep adjusting my grind setting to get the right time for my espresso, so I made opencode build something that helps me with that."

Log your espresso shots, run a simple linear regression, and get the grind setting you need to hit your target brew time.

## How it works

1. Log a shot (grind setting, dose, yield, time)
2. Pull 2+ shots at different grind settings
3. Enter your target time → app predicts the grind setting
4. Dial in, pull another, repeat until consistent

## Run

```bash
python3 server.py
# → Serving at http://localhost:8080
```

Zero dependencies — Python stdlib only (`http.server` + `sqlite3`).

## Stack

- **Backend:** one-file Python, sqlite3 persists your shots
- **Frontend:** one-file vanilla HTML/JS/CSS, no frameworks
- **Prediction:** ordinary least squares linear regression

## Notes

- Grind settings are arbitrary numbers — map them to your grinder's scale
- Regression is locally linear, sufficient for espresso tuning range
- Data stored in `shots.db` (auto-created)