import os

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dry Run Panel",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dry Run Panel")
st.caption("Sanal işlem takibi · Gerçek emir göndermez ve gerçek para kullanmaz.")


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
        st.error("Supabase verileri alınamadı. Bağlantı ve RLS ayarlarını kontrol edin.")
        with st.expander("Teknik ayrıntı"):
            st.code(str(exc))
        return pd.DataFrame()


with st.sidebar:
    st.header("Veri kaynağı")
    st.write("Supabase bağlantısı Streamlit Secrets üzerinden yapılandırılır.")
    if st.button("Verileri yenile", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption("Bu uygulama yalnızca görüntüleme yapar; alım-satım emri göndermez.")


@st.cache_data(ttl=30)
def cached_rows() -> pd.DataFrame:
    return load_rows()


df = cached_rows()
if df.empty:
    st.info(
        "Henüz gösterilecek veri yok. Supabase `public.dry_run` tablosuna "
        "`balance`, `closed`, `wins`, `losses` ve `recorded_at` alanlarıyla "
        "bir kayıt ekleyin; bağlantı ayarlarını aşağıdaki README'de bulabilirsiniz."
    )
    st.metric("Kayıt sayısı", "0")
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
        balance = float(latest["balance"])
        closed = int(latest.get("closed") or 0)
        wins = int(latest.get("wins") or 0)
        losses = int(latest.get("losses") or 0)
        cols = st.columns(4)
        cols[0].metric("Sanal bakiye", f"{balance:,.2f}")
        cols[1].metric("Kapanan işlem", f"{closed:,}")
        cols[2].metric("Kazanç", f"{wins:,}")
        cols[3].metric("Kayıp", f"{losses:,}")

    if "balance" in df and time_column in df:
        chart_data = df.dropna(subset=[time_column, "balance"]).set_index(time_column)
        if not chart_data.empty:
            st.subheader("Sanal bakiye geçmişi")
            st.line_chart(chart_data["balance"], y_label="Bakiye")

    st.subheader("Kayıtlar")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.caption("Dry Run = deneme/simülasyon. Bu panel finansal tavsiye değildir.")
