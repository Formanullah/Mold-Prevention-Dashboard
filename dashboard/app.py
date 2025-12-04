import streamlit as st
import requests
import pandas as pd
import plotly.express as px

BACKEND_URL = "http://localhost:8000"


def fetch_json(path: str):
    r = requests.get(f"{BACKEND_URL}{path}")
    r.raise_for_status()
    return r.json()


st.set_page_config(
    page_title="AERIS – Mold Risk Dashboard",
    layout="wide",
)

st.markdown(
    "<h1 style='color:#00695C;'>AERIS – Engineered for Purity</h1>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["Environment Overview", "System Health", "Alerts & Errors"])

with tab1:
    st.subheader("Room Status")

    try:
        overview = fetch_json("/api/nodes/overview")
    except Exception as e:
        st.error(f"Failed to load overview: {e}")
        overview = []

    if overview:
        df = pd.DataFrame(overview)

        cols = st.columns(len(df))
        for col, (_, row) in zip(cols, df.iterrows()):
            risk = row["risk_level"]
            status = row["status"]

            if status == "OFFLINE":
                bg = "#9E9E9E"
            elif risk == 2:
                bg = "#D32F2F"
            elif risk == 1:
                bg = "#FFA000"
            else:
                bg = "#2E7D32"

            card_html = f"""
            <div style="background:{bg};padding:16px;border-radius:12px;color:white;min-height:160px;">
              <h3>{row['node_id']}</h3>
              <p><b>Status:</b> {status}</p>
              <p><b>Mold Index:</b> {row['mold_index']:.2f}</p>
              <p><b>Temp:</b> {row['temp_1']:.1f} °C</p>
              <p><b>Humidity:</b> {row['hum_1']:.1f} %</p>
            </div>
            """
            with col:
                st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("---")
        selected_node = st.selectbox(
            "Show history for room:",
            df["node_id"].unique(),
        )

        if selected_node:
            try:
                history = fetch_json(f"/api/data/history?node_id={selected_node}")
                hdf = pd.DataFrame(history)
            except Exception as e:
                st.error(f"Failed to load history: {e}")
                hdf = pd.DataFrame()

            if not hdf.empty:
                hdf["timestamp"] = pd.to_datetime(hdf["timestamp"])

                fig_temp = px.line(
                    hdf,
                    x="timestamp",
                    y=["temp_1", "temp_2"],
                    title=f"Temperature History – {selected_node}",
                )
                st.plotly_chart(fig_temp, use_container_width=True)

                fig_hum = px.line(
                    hdf,
                    x="timestamp",
                    y=["hum_1", "hum_2"],
                    title=f"Humidity History – {selected_node}",
                )
                st.plotly_chart(fig_hum, use_container_width=True)

                fig_mold = px.line(
                    hdf,
                    x="timestamp",
                    y="mold_index",
                    title=f"Mold Index Trend – {selected_node}",
                )
                st.plotly_chart(fig_mold, use_container_width=True)
            else:
                st.info("No history yet for this node.")
    else:
        st.info("No node data available yet. Run the sample_feeder to generate data.")

with tab2:
    st.subheader("System Health (Engineering View)")

    try:
        health = fetch_json("/api/health/latest")
    except Exception as e:
        st.error(f"Failed to load health: {e}")
        health = {}

    if health:
        st.markdown("**Network Status**")
        st.json(health.get("network", {}))

        st.markdown("**Nodes**")
        nodes = health.get("nodes", {})
        rows = []
        for node_id, info in nodes.items():
            rows.append(
                {
                    "node_id": node_id,
                    "status": info.get("status"),
                    "sensors": info.get("sensors"),
                }
            )
        if rows:
            hdf = pd.DataFrame(rows)
            st.table(hdf)
        else:
            st.info("No nodes info in health report yet.")
    else:
        st.info("No health report yet.")

with tab3:
    st.subheader("Alerts & Errors")

    cols = st.columns(2)

    with cols[0]:
        st.markdown("### Recent Alerts")
        try:
            alerts = fetch_json("/api/alerts/recent")
            adf = pd.DataFrame(alerts)
            if not adf.empty:
                st.dataframe(adf)
            else:
                st.info("No alerts yet.")
        except Exception as e:
            st.error(f"Failed to load alerts: {e}")

    with cols[1]:
        st.markdown("### Recent Errors")
        try:
            errors = fetch_json("/api/errors/recent")
            edf = pd.DataFrame(errors)
            if not edf.empty:
                st.dataframe(edf)
            else:
                st.info("No errors yet.")
        except Exception as e:
            st.error(f"Failed to load errors: {e}")
