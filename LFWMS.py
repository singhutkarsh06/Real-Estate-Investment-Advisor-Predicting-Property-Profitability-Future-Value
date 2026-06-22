import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from psycopg2.extras import RealDictCursor

# ── DB CONNECTION ──
def get_connection():
    return psycopg2.connect(
        host=st.secrets["postgres"]["localhost"],
        database=st.secrets["postgres"]["Local Food Wastage Management System"],
        user=st.secrets["postgres"]["postgres"],
        password=st.secrets["postgres"]["0603"],
        port=st.secrets["postgres"]["5433"]
    )

def run_query(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return pd.DataFrame(cur.fetchall())
    finally:
        conn.close()

def run_write(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()
    finally:
        conn.close()

# ── FILTER CLAUSE BUILDER ──
# Returns (where_clause_string, params_list) for food_listings-based queries
def food_filter(city, food_type, provider_id, status=None, alias_fl="fl", alias_c="c"):
    clauses, params = [], []
    if city != "All":
        clauses.append(f"{alias_fl}.location = %s"); params.append(city)
    if food_type != "All":
        clauses.append(f"{alias_fl}.food_type = %s"); params.append(food_type)
    if provider_id is not None:
        clauses.append(f"{alias_fl}.provider_id = %s"); params.append(provider_id)
    if status and status != "All":
        clauses.append(f"LOWER({alias_c}.status) = %s"); params.append(status.lower())
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params

# ── PAGE CONFIG ──
st.set_page_config(page_title="Food Donation Dashboard", layout="wide", page_icon="🍱")

# ── CSS ──
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #2C3E50; }
  .stApp { background-color: #F5F6FA; }
  p, span, div, label, li, td, th { color: #2C3E50; }

  .progress-bar-container { background:#D5D8DC; border-radius:6px; height:10px; margin-bottom:18px; overflow:hidden; }
  .progress-bar-fill { background:linear-gradient(90deg,#2ECC71,#27AE60); height:10px; border-radius:6px; }

  .stage-card { background:white; border-radius:12px; padding:18px 10px 14px; text-align:center;
    box-shadow:0 2px 8px rgba(0,0,0,0.09); border-top:4px solid #2ECC71; }
  .stage-card.waiting { border-top-color:#BDC3C7; }
  .stage-card .stage-title { font-size:15px; font-weight:700; color:#2C3E50 !important; margin-bottom:6px; }
  .stage-card .stage-icon { font-size:30px; margin:6px 0; }
  .stage-card .stage-status { font-size:12px; color:#7F8C8D !important; font-weight:500; }
  .stage-card .stage-status.done { color:#27AE60 !important; font-weight:700; }
  .stage-card .stage-status.inprogress { color:#E67E22 !important; font-weight:700; }

  .metric-card { background:white; border-radius:12px; padding:20px 22px; box-shadow:0 2px 8px rgba(0,0,0,0.09); }
  .metric-card .m-label { font-size:12px; color:#5D6D7E !important; font-weight:600;
    text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px; }
  .metric-card .m-value { font-size:28px; font-weight:700; color:#1A252F !important; }
  .metric-card .m-sub { font-size:13px; color:#E74C3C !important; font-weight:600; margin-top:2px; }
  .metric-card .m-sub.green { color:#1E8449 !important; }

  .section-card { background:white; border-radius:12px; padding:20px 22px;
    box-shadow:0 2px 8px rgba(0,0,0,0.09); margin-bottom:16px; }
  .section-title { font-size:16px; font-weight:700; color:#1A252F !important;
    margin-bottom:14px; padding-bottom:8px; border-bottom:2px solid #EAECEE; }

  .filter-badge { background:#E8F8F0; border:1.5px solid #27AE60; color:#1E8449 !important;
    border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; display:inline-block; margin:2px; }

  .overdue-row { display:flex; align-items:center; padding:9px 0;
    border-bottom:1px solid #EAECEE; font-size:13px; color:#2C3E50 !important; }
  .overdue-row span { color:#2C3E50 !important; }
  .overdue-badge { font-weight:700; padding:3px 10px; border-radius:20px;
    font-size:12px; min-width:80px; text-align:center; margin-right:12px; }
  .badge-yellow    { background:#FEF9E7; color:#B7770D !important; border:1px solid #F9CA24; }
  .badge-orange    { background:#FEF0E6; color:#CA6F1E !important; border:1px solid #E67E22; }
  .badge-red-light { background:#FDEDEC; color:#C0392B !important; border:1px solid #E74C3C; }
  .badge-red       { background:#C0392B; color:#FFFFFF !important; }

  .workload-bar-bg   { background:#D5F5E3; border-radius:4px; height:9px; flex:1; margin:0 10px; overflow:hidden; }
  .workload-bar-fill { background:#27AE60; height:9px; border-radius:4px; }

  .stTabs [data-baseweb="tab-list"] { background:white; border-radius:10px;
    padding:4px; box-shadow:0 2px 8px rgba(0,0,0,0.07); margin-bottom:16px; }
  .stTabs [data-baseweb="tab"] { font-size:14px; font-weight:600; color:#5D6D7E !important; border-radius:8px; }
  .stTabs [aria-selected="true"] { background:#27AE60 !important; color:white !important; }

  section[data-testid="stSidebar"] { background:#2C3E50 !important; }
  section[data-testid="stSidebar"] * { color:#ECF0F1 !important; }
  section[data-testid="stSidebar"] [data-testid="stMetricValue"] { color:#2ECC71 !important; font-size:22px !important; }
  section[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color:#BDC3C7 !important; }

  [data-testid="stMetricValue"] { color:#1A252F !important; }
  [data-testid="stMetricLabel"] { color:#5D6D7E !important; }

  [data-testid="stExpander"] { background:white !important; border:1.5px solid #D5D8DC !important;
    border-radius:10px !important; margin-bottom:8px !important; }
  [data-testid="stExpander"]:hover { border-color:#27AE60 !important; }
  details summary { color:#1A252F !important; font-weight:600 !important; font-size:14px !important; }
  details summary * { color:#1A252F !important; }
  details > div * { color:#2C3E50 !important; }
  .streamlit-expanderHeader { color:#1A252F !important; font-weight:600 !important; }

  .stMarkdown p, .stMarkdown li, .stMarkdown span { color:#2C3E50 !important; }
  [data-testid="stMarkdownContainer"] * { color:#2C3E50 !important; }
  .stDataFrame td, .stDataFrame th { color:#2C3E50 !important; }
  .stRadio label, .stSelectbox label { color:#2C3E50 !important; font-weight:500; }
  .stTextInput input, .stNumberInput input, .stTextArea textarea {
    border-radius:8px !important; border:1.5px solid #D5D8DC !important;
    color:#2C3E50 !important; background:white !important; }
  .stButton > button { background:#27AE60 !important; color:white !important; border:none;
    border-radius:8px; font-weight:600; padding:8px 22px; }
  .stButton > button:hover { background:#1E8449 !important; }
  .stCaption, small { color:#5D6D7E !important; }
  hr { border:none; border-top:1.5px solid #EAECEE; margin:12px 0; }
  #MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# SIDEBAR — FILTERS
# ════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🍱 Food Donation")
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    st.caption("All charts & tables update based on your selections below.")

    cities = run_query("SELECT DISTINCT location AS city FROM food_listings ORDER BY location")
    city_list = ["All"] + cities["city"].tolist() if not cities.empty else ["All"]
    selected_city = st.selectbox("📍 City / Location", city_list)

    prov_df = run_query("SELECT provider_id, name FROM providers ORDER BY name")
    prov_map = {"All": None}
    if not prov_df.empty:
        prov_map.update(dict(zip(prov_df["name"], prov_df["provider_id"])))
    selected_provider = st.selectbox("🏪 Provider", list(prov_map.keys()))
    selected_provider_id = prov_map[selected_provider]

    ft_df = run_query("SELECT DISTINCT food_type FROM food_listings ORDER BY food_type")
    ft_list = ["All"] + ft_df["food_type"].tolist() if not ft_df.empty else ["All"]
    selected_food_type = st.selectbox("🥗 Food Type", ft_list)

    status_filter = st.selectbox("📌 Claim Status", ["All", "Completed", "Pending", "Cancelled"])

    st.markdown("---")
    # Show active filters
    active = [f for f, v in [("City", selected_city), ("Provider", selected_provider),
              ("Food Type", selected_food_type), ("Status", status_filter)] if v != "All"]
    if active:
        st.markdown("**Active Filters:**")
        for a in active:
            st.markdown(f'<span class="filter-badge">✔ {a}</span>', unsafe_allow_html=True)
    else:
        st.caption("No filters active — showing all data.")

    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    total_providers = run_query("SELECT COUNT(*) AS n FROM providers").iloc[0]["n"]
    total_receivers = run_query("SELECT COUNT(*) AS n FROM receivers").iloc[0]["n"]
    total_claims    = run_query("SELECT COUNT(*) AS n FROM claims").iloc[0]["n"]
    st.metric("Providers", total_providers)
    st.metric("Receivers", total_receivers)
    st.metric("Total Claims", total_claims)

# ════════════════════════════════════════════
# BUILD FILTERED BASE QUERIES
# Returns WHERE clauses + params for different join contexts
# ════════════════════════════════════════════
def get_food_where(table_alias="fl"):
    clauses, params = [], []
    if selected_city != "All":
        clauses.append(f"{table_alias}.location = %s"); params.append(selected_city)
    if selected_food_type != "All":
        clauses.append(f"{table_alias}.food_type = %s"); params.append(selected_food_type)
    if selected_provider_id is not None:
        clauses.append(f"{table_alias}.provider_id = %s"); params.append(selected_provider_id)
    return ("WHERE " + " AND ".join(clauses)) if clauses else "", params

def get_claims_where(fl_alias="fl", c_alias="c"):
    clauses, params = [], []
    if selected_city != "All":
        clauses.append(f"{fl_alias}.location = %s"); params.append(selected_city)
    if selected_food_type != "All":
        clauses.append(f"{fl_alias}.food_type = %s"); params.append(selected_food_type)
    if selected_provider_id is not None:
        clauses.append(f"{fl_alias}.provider_id = %s"); params.append(selected_provider_id)
    if status_filter != "All":
        clauses.append(f"LOWER({c_alias}.status) = %s"); params.append(status_filter.lower())
    return ("WHERE " + " AND ".join(clauses)) if clauses else "", params

# ── HEADER ──
st.markdown("# 🍱 Food Donation Management System")
st.markdown("Real-time analytics — use the **sidebar filters** to drill down by city, provider, food type, or claim status.")

# ── PROGRESS BAR (filtered) ──
fw, fp = get_food_where()
comp_sql = f"""
    SELECT COUNT(*) AS n FROM claims c
    JOIN food_listings fl ON c.food_id = fl.food_id
    {fw} {"AND" if fw else "WHERE"} LOWER(c.status)='completed'
""" if fw else "SELECT COUNT(*) AS n FROM claims WHERE LOWER(status)='completed'"
comp_params = fp if fw else None
completed = run_query(comp_sql, comp_params).iloc[0]["n"]

total_sql = f"""
    SELECT COUNT(*) AS n FROM claims c
    JOIN food_listings fl ON c.food_id = fl.food_id {fw}
""" if fw else "SELECT COUNT(*) AS n FROM claims"
total_filtered = run_query(total_sql, fp if fw else None).iloc[0]["n"]
pct = round(completed / total_filtered * 100) if total_filtered else 0

st.markdown(f"""
<div class="progress-bar-container">
  <div class="progress-bar-fill" style="width:{pct}%"></div>
</div>
""", unsafe_allow_html=True)

# ── STAGE CARDS ──
food_where, food_params = get_food_where()
total_food_filtered = run_query(
    f"SELECT SUM(quantity) AS n FROM food_listings fl {food_where}", food_params
).iloc[0]["n"] or 0

c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1.2])
with c1:
    st.markdown("""<div class="stage-card"><div class="stage-title">Data Loaded</div>
        <div class="stage-icon">✅</div><div class="stage-status done">Completed</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="stage-card"><div class="stage-title">Cleaned</div>
        <div class="stage-icon">✅</div><div class="stage-status done">Completed</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="stage-card"><div class="stage-title">Claims</div>
        <div class="stage-icon" style="font-size:22px;font-weight:700;color:#E67E22">{pct}%</div>
        <div class="stage-status inprogress">In Progress</div></div>""", unsafe_allow_html=True)
with c4:
    st.markdown("""<div class="stage-card waiting"><div class="stage-title">Analysis</div>
        <div class="stage-icon">🕐</div><div class="stage-status">Waiting</div></div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="stage-card" style="background:#2ECC71;border-top-color:#27AE60">
        <div class="stage-title" style="color:white">Filtered Food</div>
        <div style="font-size:26px;font-weight:700;color:white">{int(total_food_filtered):,}</div>
        <div style="font-size:12px;color:#D5F5E3">units available</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──
tabs = st.tabs(["📊 Dashboard", "📋 15 Queries", "🗃️ Browse Data", "✏️ CRUD", "📞 Contacts"])

# ════════════════════════════════════════════
# TAB 1 — DASHBOARD (all queries use filters)
# ════════════════════════════════════════════
with tabs[0]:

    # ── Metric Cards ──
    cw, cp = get_claims_where()

    pending_sql = f"""SELECT COUNT(*) AS n FROM claims c
        JOIN food_listings fl ON c.food_id=fl.food_id
        {cw} {"AND" if cw else "WHERE"} LOWER(c.status)='pending'"""
    pending_p = cp + ["pending"] if cp else None

    cancelled_sql = f"""SELECT COUNT(*) AS n FROM claims c
        JOIN food_listings fl ON c.food_id=fl.food_id
        {cw} {"AND" if cw else "WHERE"} LOWER(c.status)='cancelled'"""
    cancelled_p = cp + ["cancelled"] if cp else None

    waste_sql = f"""SELECT COUNT(*) AS n FROM food_listings fl
        LEFT JOIN claims c ON fl.food_id=c.food_id
        {food_where} {"AND" if food_where else "WHERE"} c.claim_id IS NULL"""

    pending_count   = run_query(pending_sql,   cp).iloc[0]["n"]
    cancelled_count = run_query(cancelled_sql, cp).iloc[0]["n"]
    waste_count     = run_query(waste_sql, food_params).iloc[0]["n"]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card"><div class="m-label">Food Available</div>
            <div class="m-value">{int(total_food_filtered):,}</div>
            <div class="m-sub green">filtered units</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card"><div class="m-label">Completed Claims</div>
            <div class="m-value">{int(completed):,}</div>
            <div class="m-sub green">{pct}% success rate</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card"><div class="m-label">Pending Claims</div>
            <div class="m-value">{int(pending_count):,}</div>
            <div class="m-sub">awaiting fulfillment</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card"><div class="m-label">Unclaimed Listings</div>
            <div class="m-value">{int(waste_count):,}</div>
            <div class="m-sub">potential waste</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row 1 ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-card"><div class="section-title">Provider Type — Food Contributed</div>', unsafe_allow_html=True)
        df_ptype = run_query(f"""
            SELECT p.type AS provider_type, SUM(fl.quantity) AS total_quantity
            FROM food_listings fl JOIN providers p ON fl.provider_id=p.provider_id
            {food_where}
            GROUP BY p.type ORDER BY total_quantity DESC
        """, food_params)
        if not df_ptype.empty:
            fig = px.bar(df_ptype, x="provider_type", y="total_quantity",
                color_discrete_sequence=["#2ECC71","#27AE60","#1ABC9C","#16A085"],
                labels={"provider_type":"Provider Type","total_quantity":"Total Quantity"})
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=10,b=10,l=0,r=0), showlegend=False, font=dict(family="Inter"),
                xaxis=dict(title=""), yaxis=dict(title="Quantity", gridcolor="#F0F0F0"))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for selected filters.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card"><div class="section-title">Claim Status Breakdown</div>', unsafe_allow_html=True)
        df_status = run_query(f"""
            SELECT c.status, COUNT(*) AS total
            FROM claims c JOIN food_listings fl ON c.food_id=fl.food_id
            {food_where}
            GROUP BY c.status
        """, food_params)
        if not df_status.empty:
            fig = px.pie(df_status, names="status", values="total", hole=0.55,
                color_discrete_map={"Completed":"#2ECC71","Pending":"#F39C12","Cancelled":"#E74C3C"})
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=10,b=10,l=0,r=0), font=dict(family="Inter"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2))
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for selected filters.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Charts Row 2 ──
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-card"><div class="section-title">Top Unclaimed Food (Potential Waste)</div>', unsafe_allow_html=True)
        df_waste = run_query(f"""
            SELECT fl.food_name, fl.expiry_date, fl.location, p.name AS provider
            FROM food_listings fl
            JOIN providers p ON fl.provider_id=p.provider_id
            LEFT JOIN claims c ON fl.food_id=c.food_id
            {food_where} {"AND" if food_where else "WHERE"} c.claim_id IS NULL
            ORDER BY fl.expiry_date ASC LIMIT 5
        """, food_params)
        if not df_waste.empty:
            badges = ["badge-yellow","badge-orange","badge-red-light","badge-red","badge-red"]
            labels = ["Expiring Soon","Overdue","Overdue","Critical","Critical"]
            for i, row in df_waste.iterrows():
                b = badges[min(i,4)]; l = labels[min(i,4)]
                st.markdown(f"""<div class="overdue-row">
                  <span class="overdue-badge {b}">{l}</span>
                  <span style="flex:1;color:#2C3E50;font-weight:500">{row['food_name']}</span>
                  <span style="color:#7F8C8D;margin-right:10px;font-size:12px">{row['expiry_date']}</span>
                  <span style="color:#2C3E50;font-weight:600;font-size:12px">{str(row['provider'])[:14]}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.success("✅ No unclaimed food for selected filters!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="section-card"><div class="section-title">Meal Type Claim Workload</div>', unsafe_allow_html=True)
        df_meal = run_query(f"""
            SELECT fl.meal_type, COUNT(c.claim_id) AS total_claims
            FROM claims c JOIN food_listings fl ON c.food_id=fl.food_id
            {food_where}
            GROUP BY fl.meal_type ORDER BY total_claims DESC
        """, food_params)
        if not df_meal.empty:
            max_c = df_meal["total_claims"].max()
            for _, row in df_meal.iterrows():
                pb = int(row["total_claims"] / max_c * 100)
                st.markdown(f"""<div class="overdue-row">
                  <span style="min-width:80px;color:#2C3E50;font-weight:600">{row['meal_type']}</span>
                  <div class="workload-bar-bg"><div class="workload-bar-fill" style="width:{pb}%"></div></div>
                  <span style="color:#27AE60;font-weight:700;min-width:50px;text-align:right">{row['total_claims']:,}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No data for selected filters.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Charts Row 3 ──
    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<div class="section-card"><div class="section-title">Top 10 Providers by Quantity Donated</div>', unsafe_allow_html=True)
        df_top_prov = run_query(f"""
            SELECT p.name, SUM(fl.quantity) AS total
            FROM providers p JOIN food_listings fl ON p.provider_id=fl.provider_id
            {food_where}
            GROUP BY p.name ORDER BY total DESC LIMIT 10
        """, food_params)
        if not df_top_prov.empty:
            fig = px.bar(df_top_prov, x="total", y="name", orientation="h",
                color="total", color_continuous_scale=["#A9DFBF","#2ECC71","#1A8A4A"],
                labels={"total":"Quantity","name":""})
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=5,b=5,l=0,r=0), coloraxis_showscale=False,
                font=dict(family="Inter"), yaxis=dict(autorange="reversed"),
                xaxis=dict(gridcolor="#F0F0F0"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for selected filters.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="section-card"><div class="section-title">Top Receivers Activity</div>', unsafe_allow_html=True)
        df_recv = run_query(f"""
            SELECT r.name AS receiver, r.type, COUNT(c.claim_id) AS claims
            FROM claims c
            JOIN receivers r ON c.receiver_id=r.receiver_id
            JOIN food_listings fl ON c.food_id=fl.food_id
            {food_where}
            GROUP BY r.name, r.type ORDER BY claims DESC LIMIT 5
        """, food_params)
        if not df_recv.empty:
            max_r = df_recv["claims"].max()
            st.markdown("""<div class="overdue-row" style="font-weight:700;color:#7F8C8D !important;font-size:11px;text-transform:uppercase">
              <span style="flex:1;color:#7F8C8D !important">Receiver</span>
              <span style="min-width:70px;color:#7F8C8D !important">Type</span>
              <span style="min-width:100px;color:#7F8C8D !important">Volume</span>
              <span style="min-width:50px;text-align:right;color:#7F8C8D !important">Claims</span>
            </div>""", unsafe_allow_html=True)
            for _, row in df_recv.iterrows():
                pb = int(row["claims"] / max_r * 100)
                st.markdown(f"""<div class="overdue-row">
                  <span style="flex:1;color:#2C3E50;font-weight:600">{str(row['receiver'])[:16]}</span>
                  <span style="min-width:70px;color:#7F8C8D;font-size:12px">{row['type']}</span>
                  <div class="workload-bar-bg" style="min-width:100px">
                    <div class="workload-bar-fill" style="width:{pb}%"></div></div>
                  <span style="color:#27AE60;font-weight:700;min-width:50px;text-align:right">{row['claims']}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No receiver data for selected filters.")
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 2 — 15 QUERIES (filtered)
# ════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    if active:
        st.markdown(f"**Active filters:** {', '.join(active)} — query results reflect your selections.")
    else:
        st.markdown("Showing **all data** — use sidebar filters to narrow results.")
    st.markdown('</div>', unsafe_allow_html=True)

    fw, fp = get_food_where()
    cw, cp = get_claims_where()
    and_fw = ("AND" if fw else "WHERE")

    queries = {
        "Q1 — Providers & Receivers per City": (
            "SELECT city,'Provider' AS role,COUNT(*) AS total FROM providers GROUP BY city UNION ALL SELECT city,'Receiver' AS role,COUNT(*) AS total FROM receivers GROUP BY city ORDER BY city,role", None),
        "Q2 — Provider Type Contributing Most Food": (
            f"SELECT p.type AS provider_type,SUM(fl.quantity) AS total_quantity FROM food_listings fl JOIN providers p ON fl.provider_id=p.provider_id {fw} GROUP BY p.type ORDER BY total_quantity DESC", fp),
        "Q3 — Provider Contact Info": (
            f"SELECT name,type,city,contact FROM providers {'WHERE city=%s' if selected_city!='All' else ''} ORDER BY name",
            [selected_city] if selected_city!="All" else None),
        "Q4 — Receivers with Most Claims": (
            f"SELECT r.name,r.type,COUNT(c.claim_id) AS total_claims FROM claims c JOIN receivers r ON c.receiver_id=r.receiver_id JOIN food_listings fl ON c.food_id=fl.food_id {cw} GROUP BY r.receiver_id,r.name,r.type ORDER BY total_claims DESC LIMIT 20", cp),
        "Q5 — Total Food Available": (
            f"SELECT SUM(quantity) AS total_food_available FROM food_listings fl {fw}", fp),
        "Q6 — City with Most Food Listings": (
            f"SELECT location AS city,COUNT(food_id) AS total_listings,SUM(quantity) AS total_quantity FROM food_listings fl {fw} GROUP BY location ORDER BY total_listings DESC LIMIT 20", fp),
        "Q7 — Most Common Food Types": (
            f"SELECT food_type,COUNT(food_id) AS listing_count,SUM(quantity) AS total_quantity FROM food_listings fl {fw} GROUP BY food_type ORDER BY listing_count DESC", fp),
        "Q8 — Claims per Food Item": (
            f"SELECT fl.food_name,fl.food_type,COUNT(c.claim_id) AS total_claims FROM food_listings fl LEFT JOIN claims c ON fl.food_id=c.food_id {fw} GROUP BY fl.food_id,fl.food_name,fl.food_type ORDER BY total_claims DESC LIMIT 20", fp),
        "Q9 — Provider with Most Successful Claims": (
            f"SELECT p.name,p.type,COUNT(c.claim_id) AS completed_claims FROM claims c JOIN food_listings fl ON c.food_id=fl.food_id JOIN providers p ON fl.provider_id=p.provider_id {fw} {and_fw} LOWER(c.status)='completed' GROUP BY p.provider_id,p.name,p.type ORDER BY completed_claims DESC LIMIT 10",
            fp + [] if fp else None),
        "Q10 — Claim Status Percentage": (
            f"SELECT c.status,COUNT(*) AS total,ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(),2) AS percentage FROM claims c JOIN food_listings fl ON c.food_id=fl.food_id {fw} GROUP BY c.status ORDER BY total DESC", fp),
        "Q11 — Avg Quantity per Receiver": (
            f"SELECT r.name,COUNT(c.claim_id) AS total_claims,ROUND(AVG(fl.quantity),2) AS avg_quantity FROM claims c JOIN receivers r ON c.receiver_id=r.receiver_id JOIN food_listings fl ON c.food_id=fl.food_id {cw} GROUP BY r.receiver_id,r.name ORDER BY avg_quantity DESC LIMIT 20", cp),
        "Q12 — Most Claimed Meal Type": (
            f"SELECT fl.meal_type,COUNT(c.claim_id) AS total_claims FROM claims c JOIN food_listings fl ON c.food_id=fl.food_id {cw} GROUP BY fl.meal_type ORDER BY total_claims DESC", cp),
        "Q13 — Total Quantity Donated per Provider": (
            f"SELECT p.name,p.type,p.city,SUM(fl.quantity) AS total_donated,COUNT(fl.food_id) AS listings FROM providers p JOIN food_listings fl ON p.provider_id=fl.provider_id {fw} GROUP BY p.provider_id,p.name,p.type,p.city ORDER BY total_donated DESC", fp),
        "Q14 — Food Wastage (No Claims)": (
            f"SELECT fl.food_name,fl.quantity,fl.expiry_date,fl.location,p.name AS provider_name FROM food_listings fl JOIN providers p ON fl.provider_id=p.provider_id LEFT JOIN claims c ON fl.food_id=c.food_id {fw} {and_fw} c.claim_id IS NULL ORDER BY fl.expiry_date ASC", fp),
        "Q15 — Highest Demand Locations": (
            f"SELECT fl.location AS city,COUNT(c.claim_id) AS total_claims,SUM(fl.quantity) AS total_food_claimed FROM claims c JOIN food_listings fl ON c.food_id=fl.food_id {fw} {and_fw} LOWER(c.status)='completed' GROUP BY fl.location ORDER BY total_claims DESC LIMIT 20", fp),
    }

    for i, (title, (sql, params)) in enumerate(queries.items(), 1):
        with st.expander(f"Q{i} — {title.split('—')[-1].strip()}"):
            st.markdown(f"<p style='color:#27AE60;font-weight:700;font-size:13px'>🔹 {title}</p>", unsafe_allow_html=True)
            try:
                df = run_query(sql, params)
                st.dataframe(df, use_container_width=True, height=260)
                st.markdown(f"<p style='color:#5D6D7E;font-size:12px'>✅ {len(df)} rows returned</p>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

# ════════════════════════════════════════════
# TAB 3 — BROWSE DATA (filtered)
# ════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    table_choice = st.radio("Select Table", ["food_listings","claims","providers","receivers"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if table_choice == "food_listings":
        sql = "SELECT * FROM food_listings WHERE 1=1"; params = []
        if selected_city != "All":       sql += " AND location=%s";    params.append(selected_city)
        if selected_food_type != "All":  sql += " AND food_type=%s";   params.append(selected_food_type)
        if selected_provider_id is not None: sql += " AND provider_id=%s"; params.append(selected_provider_id)
    elif table_choice == "claims":
        sql = """SELECT c.* FROM claims c JOIN food_listings fl ON c.food_id=fl.food_id WHERE 1=1"""; params = []
        if selected_city != "All":       sql += " AND fl.location=%s"; params.append(selected_city)
        if selected_food_type != "All":  sql += " AND fl.food_type=%s";params.append(selected_food_type)
        if selected_provider_id is not None: sql += " AND fl.provider_id=%s"; params.append(selected_provider_id)
        if status_filter != "All":       sql += " AND LOWER(c.status)=%s"; params.append(status_filter.lower())
    elif table_choice == "providers":
        sql = "SELECT * FROM providers WHERE 1=1"; params = []
        if selected_city != "All": sql += " AND city=%s"; params.append(selected_city)
        if selected_provider_id is not None: sql += " AND provider_id=%s"; params.append(selected_provider_id)
    else:
        sql = "SELECT * FROM receivers WHERE 1=1"; params = []
        if selected_city != "All": sql += " AND city=%s"; params.append(selected_city)

    try:
        df = run_query(sql, params or None)
        st.dataframe(df, use_container_width=True, height=450)
        col_a, col_b = st.columns([3,1])
        col_a.caption(f"**{len(df)} rows** matched your filters")
        col_b.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(),
            file_name=f"{table_choice}_filtered.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Query error: {e}")

# ════════════════════════════════════════════
# TAB 4 — CRUD
# ════════════════════════════════════════════
with tabs[3]:
    crud_table = st.selectbox("Table", ["food_listings","providers","receivers","claims"])
    crud_op = st.radio("Operation", ["➕ Insert","✏️ Update","🗑️ Delete"], horizontal=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    if crud_op == "➕ Insert":
        if crud_table == "food_listings":
            c1,c2 = st.columns(2)
            fn=c1.text_input("Food Name"); qty=c2.number_input("Quantity",min_value=1)
            exp=c1.date_input("Expiry Date"); pid=c2.number_input("Provider ID",min_value=1,step=1)
            pt=c1.selectbox("Provider Type",["Restaurant","Grocery Store","Supermarket","Bakery","Other"])
            loc=c2.text_input("Location")
            ft=c1.selectbox("Food Type",["Vegetarian","Non-Vegetarian","Vegan"])
            mt=c2.selectbox("Meal Type",["Breakfast","Lunch","Dinner","Snacks"])
            if st.button("Add Food Listing"):
                run_write("INSERT INTO food_listings(food_name,quantity,expiry_date,provider_id,provider_type,location,food_type,meal_type) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(fn,qty,exp,pid,pt,loc,ft,mt))
                st.success("✅ Food listing added!")
        elif crud_table == "providers":
            c1,c2=st.columns(2)
            nm=c1.text_input("Name"); pt=c2.selectbox("Type",["Restaurant","Grocery Store","Supermarket","Bakery","Other"])
            addr=st.text_area("Address"); ct=c1.text_input("City"); con=c2.text_input("Contact")
            if st.button("Add Provider"):
                run_write("INSERT INTO providers(name,type,address,city,contact) VALUES(%s,%s,%s,%s,%s)",(nm,pt,addr,ct,con))
                st.success("✅ Provider added!")
        elif crud_table == "receivers":
            c1,c2=st.columns(2)
            nm=c1.text_input("Name"); rt=c2.selectbox("Type",["Individual","Shelter","NGO","Community Center"])
            ct=c1.text_input("City"); con=c2.text_input("Contact")
            if st.button("Add Receiver"):
                run_write("INSERT INTO receivers(name,type,city,contact) VALUES(%s,%s,%s,%s)",(nm,rt,ct,con))
                st.success("✅ Receiver added!")
        elif crud_table == "claims":
            c1,c2=st.columns(2)
            fid=c1.number_input("Food ID",min_value=1,step=1); rid=c2.number_input("Receiver ID",min_value=1,step=1)
            st_=st.selectbox("Status",["Pending","Completed","Cancelled"])
            if st.button("Add Claim"):
                run_write("INSERT INTO claims(food_id,receiver_id,status,claim_timestamp) VALUES(%s,%s,%s,NOW())",(fid,rid,st_))
                st.success("✅ Claim added!")

    elif crud_op == "✏️ Update":
        if crud_table == "claims":
            cid=st.number_input("Claim ID",min_value=1,step=1); ns=st.selectbox("New Status",["Pending","Completed","Cancelled"])
            if st.button("Update"):
                run_write("UPDATE claims SET status=%s WHERE claim_id=%s",(ns,cid)); st.success(f"✅ Claim {cid} → {ns}")
        elif crud_table == "food_listings":
            fid=st.number_input("Food ID",min_value=1,step=1); nq=st.number_input("New Quantity",min_value=0)
            if st.button("Update"):
                run_write("UPDATE food_listings SET quantity=%s WHERE food_id=%s",(nq,fid)); st.success(f"✅ Food ID {fid} qty → {nq}")
        elif crud_table == "providers":
            pid=st.number_input("Provider ID",min_value=1,step=1); nc=st.text_input("New Contact")
            if st.button("Update"):
                run_write("UPDATE providers SET contact=%s WHERE provider_id=%s",(nc,pid)); st.success(f"✅ Provider {pid} updated")
        elif crud_table == "receivers":
            rid=st.number_input("Receiver ID",min_value=1,step=1); nc=st.text_input("New Contact")
            if st.button("Update"):
                run_write("UPDATE receivers SET contact=%s WHERE receiver_id=%s",(nc,rid)); st.success(f"✅ Receiver {rid} updated")

    elif crud_op == "🗑️ Delete":
        st.warning("⚠️ Permanent — cannot be undone.")
        if crud_table=="claims":
            cid=st.number_input("Claim ID",min_value=1,step=1)
            if st.button("Delete",type="primary"):
                run_write("DELETE FROM claims WHERE claim_id=%s",(cid,)); st.success(f"🗑️ Claim {cid} deleted")
        elif crud_table=="food_listings":
            fid=st.number_input("Food ID",min_value=1,step=1)
            if st.button("Delete",type="primary"):
                run_write("DELETE FROM food_listings WHERE food_id=%s",(fid,)); st.success(f"🗑️ Food {fid} deleted")
        elif crud_table=="providers":
            pid=st.number_input("Provider ID",min_value=1,step=1)
            if st.button("Delete",type="primary"):
                run_write("DELETE FROM providers WHERE provider_id=%s",(pid,)); st.success(f"🗑️ Provider {pid} deleted")
        elif crud_table=="receivers":
            rid=st.number_input("Receiver ID",min_value=1,step=1)
            if st.button("Delete",type="primary"):
                run_write("DELETE FROM receivers WHERE receiver_id=%s",(rid,)); st.success(f"🗑️ Receiver {rid} deleted")

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 5 — CONTACTS
# ════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    dtype = st.radio("Directory", ["Providers","Receivers"], horizontal=True)
    search = st.text_input("🔍 Search by name or city")
    st.markdown('</div>', unsafe_allow_html=True)

    if dtype == "Providers":
        sql = "SELECT name,type,city,contact,address FROM providers WHERE 1=1"; params=[]
        if selected_city != "All": sql += " AND city=%s"; params.append(selected_city)
        if selected_provider_id is not None: sql += " AND provider_id=%s"; params.append(selected_provider_id)
    else:
        sql = "SELECT name,type,city,contact FROM receivers WHERE 1=1"; params=[]
        if selected_city != "All": sql += " AND city=%s"; params.append(selected_city)

    if search:
        sql += " AND (LOWER(name) LIKE %s OR LOWER(city) LIKE %s)"
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])

    try:
        df = run_query(sql, params or None)
        st.dataframe(df, use_container_width=True, height=500)
        st.caption(f"**{len(df)}** contacts found")
    except Exception as e:
        st.error(f"Error: {e}")