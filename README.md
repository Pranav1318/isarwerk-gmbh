# Isarwerk Präzision — "What is BLP worth?" CFO calculator

A 2-minute value calculator for a fictional German manufacturer (€320M revenue, ~60,600 supplier invoices a year, SAP S/4HANA).
Built from public information only. Pick a scenario, change any number on the left, and see hours saved, cash value, payback and the most BLP could cost before it stops paying off.

## Files
- `app.py` — the Streamlit app (CFO-facing)
- `model_config.py` — every assumption and the calculation (same logic as the Excel model)
- `Isarwerk_AP_Value_Model.xlsx` — all assumptions with basis, rationale, source link and confidence; live formulas; sanity checks
- `requirements.txt`, `.streamlit/config.toml` — dependencies and light theme

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (public link)
1. Push these files to a GitHub repository.
2. Go to https://share.streamlit.io, sign in with GitHub, choose the repo, branch and `app.py`.
3. Deploy, then open the `*.streamlit.app` URL in a private window to confirm it is public.

## How the number is built
Invoices by type → manual hours today → hours with BLP (share handled end-to-end + minutes a person still needs) → hours saved → € value → share that becomes cash → minus BLP fee (placeholder).
Saved time is not cash: the app and Excel show both. BLP publishes no prices, so the fee is a placeholder and the app shows the break-even price instead.
