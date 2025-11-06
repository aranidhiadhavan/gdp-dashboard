import streamlit as st
import pandas as pd
import plotly.express as px
import math
from databricks import sql

# ---------------------------------------------------
# Read URL query parameters
# ---------------------------------------------------
params = st.experimental_get_query_params()
user = params.get("user", ["unknown"])[0]
workspace = params.get("workspace", ["none"])[0]
run = params.get("run", ["none"])[0]

# ---------------------------------------------------
# Streamlit Config
# ---------------------------------------------------
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:',
)

# ---------------------------------------------------
# Display context info passed from Databricks
# ---------------------------------------------------
st.title(":earth_americas: GDP Dashboard")
st.write(f"👤 **User:** `{user}`")
st.write(f"🏢 **Workspace:** `{workspace}`")
st.write(f"🔁 **Run ID:** `{run}`")
st.write("---")

# ---------------------------------------------------
# Live Databricks SQL Warehouse query
# ---------------------------------------------------
try:
    conn = sql.connect(
        server_hostname=st.secrets["DATABRICKS_HOST"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"]
    )

    query = """
        SELECT country, year, gdp, growth_pct, rank
        FROM gdp_latest_results
        ORDER BY rank
    """

    live_df = pd.read_sql(query, conn)
    conn.close()

    st.success("✅ Live data retrieved from the Databricks workspace!")
    st.dataframe(live_df)

except Exception as e:
    st.error("❌ Failed to fetch live data from Databricks.")
    st.write(e)
    live_df = None

# Only draw charts if data loaded
if live_df is not None and len(live_df) > 0:

    # ---------------------------------------------------
    # Bar chart showing GDP ranking
    # ---------------------------------------------------
    st.header("Top Countries by GDP (Latest Year)")
    fig = px.bar(live_df, x='country', y='gdp', title='GDP Ranking', text='gdp')
    st.plotly_chart(fig)

    # ---------------------------------------------------
    # Growth scatter visualization
    # ---------------------------------------------------
    st.header("GDP Growth % Comparison")
    fig2 = px.scatter(
        live_df,
        x="gdp",
        y="growth_pct",
        color="country",
        size="gdp",
        title="GDP vs Growth Percentage"
    )
    st.plotly_chart(fig2)

    # ---------------------------------------------------
    # Interactive country selector
    # ---------------------------------------------------
    st.header("Select a country to review:")
    selected_country = st.selectbox("Country", live_df['country'].unique())
    st.write(live_df[live_df['country'] == selected_country])

else:
    st.info("Run your Databricks notebook first to populate results → then refresh here!")
