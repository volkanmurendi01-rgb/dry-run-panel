import os

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dry Run Panel",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dry Run Panel")
st.caption("Virtual trade tracking · It does not send real orders or use real money.")


def get_setting(name: str):
    """Read a setting from Streamlit Secrets first, then environment variables."""
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except (FileNotFoundError, KeyError):
        pass
    return os.getenv(name)


def load_rows() -> pd.DataFrame:
    url = get_setting("SUPABASE_URL")
    key = get_setting("SUPABASE_ANON_KEY")
    if not url or not key:
        return pd.DataFrame()

    try:
        from supabase import create_client

        client = create_client(url, key)
        response = (
            client.table("dry_run")
            .select("balance, closed, wins, losses, recorded_at, created_at")
            .order("recorded_at", desc=False)
            .limit(5000)
            .execute()
        )
        return pd.DataFrame(response.data or [])
    except Exception as exc:
        st.error("Supabase data could not be loaded. Check your connection and RLS settings.")
        with st.expander("Technical details"):
            st.code(str(exc))
        return pd.DataFrame()


with st.sidebar:
    st.header("Data source")
    st.write("The Supabase connection is configured through Streamlit Secrets.")
    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption("This app is view-only; it does not send trading orders.")


@st.cache_data(ttl=30)
def cached_rows() -> pd.DataFrame:
    return load_rows()


df = cached_rows()
if df.empty:
    st.info(
        "There is no data to display yet. Add a record to the Supabase "
        "`public.dry_run` table with `balance`, `closed`, `wins`, `losses`, "
        "and `recorded_at` fields. Connection settings are available in the README."
    )
    st.metric("Record count", "0")
else:
    for column in ("balance", "closed", "wins", "losses"):
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if "recorded_at" in df and df["recorded_at"].notna().any():
        df["recorded_at"] = pd.to_datetime(df["recorded_at"], errors="coerce", utc=True)
        time_column = "recorded_at"
    else:
        df["created_at"] = pd.to_datetime(df.get("created_at"), errors="coerce", utc=True)
        time_column = "created_at"

    latest = df.dropna(subset=["balance"]).iloc[-1] if df["balance"].notna().any() else None
    if latest is not None:
        closed = int(latest.get("closed") or 0)
        wins = int(latest.get("wins") or 0)
        losses = int(latest.get("losses") or 0)
        cols = st.columns(3)
        cols[0].metric("Closed trades", f"{closed:,}")
        cols[1].metric("Wins", f"{wins:,}")
        cols[2].metric("Losses", f"{losses:,}")

    if "balance" in df and time_column in df:
        chart_data = df.dropna(subset=[time_column, "balance"]).set_index(time_column)
        if not chart_data.empty:
            st.subheader("Virtual balance history")
            st.line_chart(chart_data["balance"], y_label="Balance")

    st.subheader("Records")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.caption("Dry Run = trial/simulation. This panel is not financial advice.")
