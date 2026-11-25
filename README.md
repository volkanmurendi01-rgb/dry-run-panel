# Dry Run Panel

A simple panel that reads dry-run trading data from Supabase and displays it in Streamlit. The app only reads data and never sends real trading orders.

## Local setup

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Supabase connection

Add the following values to the Streamlit app settings under **Secrets**. Do not place the Supabase URL or anon/publishable key in source code or GitHub.

```toml
SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_OR_PUBLISHABLE_KEY"
```

The app reads `balance`, `closed`, `wins`, `losses`, `recorded_at`, and `created_at` from `public.dry_run`. Configure Data API access and an appropriate `SELECT` RLS policy for the table.

## Streamlit Community Cloud

1. Select this GitHub repository in Streamlit Community Cloud.
2. Set `app.py` as the main file.
3. Add the TOML values above under the app's **Secrets** settings.
4. Deploy the app. It will show an empty-state message until data is available.
