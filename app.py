import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import datetime
import warnings
warnings.filterwarnings('ignore')

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="PropIntel · India Real Estate",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=IBM+Plex+Mono:wght@400;600&family=Mulish:wght@300;400;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Mulish', sans-serif !important; }
.stApp { background-color: #0e0e11 !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

.masthead {
    background: linear-gradient(105deg, #0e0e11 0%, #12120f 40%, #1a1500 100%);
    border-bottom: 1px solid #2a2a35;
    padding: 24px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -2rem 28px -2rem;
}
.brand-name {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 900;
    color: #ffffff;
}
.brand-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #f0a500;
    border: 1px solid #c47e00;
    padding: 3px 8px;
    border-radius: 3px;
    margin-left: 10px;
}
.masthead-stats { display: flex; gap: 32px; }
.mstat-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
}
.mstat-lbl {
    font-size: 10px;
    color: #6b6b7a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

.kpi {
    background: #16161a;
    border: 1px solid #2a2a35;
    border-radius: 12px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}
.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: #f0a500;
}
.kpi-icon { font-size: 22px; margin-bottom: 8px; display: block; }
.kpi-num {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
}
.kpi-lbl {
    font-size: 10px;
    color: #6b6b7a;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 4px;
}
.kpi-delta { font-family: 'IBM Plex Mono', monospace; font-size: 11px; margin-top: 6px; }
.up { color: #34d399; }
.down { color: #f87171; }

.panel {
    background: #16161a;
    border: 1px solid #2a2a35;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 20px;
}
.panel-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #6b6b7a;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #2a2a35;
}

.sec-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #f0a500;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sec-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #2a2a35;
    margin-left: 12px;
}

/* Classification result */
.clf-good {
    background: linear-gradient(135deg, #052e1c, #065f46);
    border: 2px solid #34d399;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.clf-bad {
    background: linear-gradient(135deg, #2d0a0a, #450a0a);
    border: 2px solid #f87171;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.clf-icon { font-size: 40px; display: block; margin-bottom: 8px; }
.clf-title {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    color: #ffffff;
    font-weight: 700;
}
.clf-sub { font-size: 12px; color: rgba(255,255,255,0.55); margin-top: 6px; }
.clf-conf {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 20px;
    font-weight: 700;
    margin-top: 12px;
}

/* Regression result */
.reg-card {
    background: linear-gradient(135deg, #1a1200, #2d1f00);
    border: 2px solid #f0a500;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.reg-title {
    font-size: 11px;
    color: #f0a500;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'IBM Plex Mono', monospace;
}
.reg-val {
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 900;
    color: #ffffff;
    margin: 8px 0;
}
.reg-sub { font-size: 12px; color: rgba(255,255,255,0.5); }

/* Confidence bar */
.conf-bar-bg {
    background: #2a2a35;
    border-radius: 8px;
    height: 12px;
    width: 100%;
    margin-top: 10px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.5s ease;
}

.stat-pill {
    background: #1c1c22;
    border: 1px solid #2a2a35;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}
.pill-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 18px;
    font-weight: 600;
    color: #f0a500;
}
.pill-lbl {
    font-size: 10px;
    color: #6b6b7a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 5px;
}

div[data-testid="stTabs"] button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #6b6b7a !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #f0a500 !important;
    border-bottom-color: #f0a500 !important;
}
div[data-testid="stButton"] > button {
    background: #f0a500 !important;
    color: #0e0e11 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 14px 32px !important;
}
label[data-testid="stWidgetLabel"] p {
    font-size: 10px !important;
    color: #6b6b7a !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}
</style>
""", unsafe_allow_html=True)

# ── MATPLOTLIB DARK THEME ─────────────────────────────────
BG     = '#16161a'
BORDER = '#2a2a35'
AMBER  = '#f0a500'
GREEN  = '#34d399'
RED    = '#f87171'
BLUE   = '#60a5fa'
MUTED  = '#6b6b7a'
WHITE  = '#e8e6e0'
PURPLE = '#a78bfa'
PALETTE= [AMBER, GREEN, BLUE, RED, PURPLE, '#fb923c', '#38bdf8']

plt.rcParams.update({
    'figure.facecolor': BG, 'axes.facecolor': BG,
    'axes.edgecolor': BORDER, 'axes.labelcolor': MUTED,
    'xtick.color': MUTED, 'ytick.color': MUTED,
    'text.color': WHITE, 'grid.color': BORDER,
    'grid.linewidth': 0.5, 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.spines.left': False,
})

# ── LOAD ──────────────────────────────────────────────────
@st.cache_resource
def load_models():
    with open('model_classification_rf.pkl', 'rb') as f:
        clf = pickle.load(f)
    with open('model_regression_xgb.pkl', 'rb') as f:
        reg = pickle.load(f)
    with open('label_encoders.pkl', 'rb') as f:
        enc = pickle.load(f)
    return clf, reg, enc

@st.cache_data
def load_data():
    return pd.read_csv('india_housing_eda.csv')

clf, reg, encoders = load_models()
df = load_data()

FEATURES = ['BHK','Size_in_SqFt','Price_in_Lakhs','Price_per_SqFt_calc',
            'Floor_No','Total_Floors','Floor_Ratio','Property_Age',
            'Nearby_Schools','Nearby_Hospitals','Transport_Score',
            'Infrastructure_Score','Amenities_Count','School_Density_Score',
            'State','City','Property_Type','Furnished_Status',
            'Facing','Owner_Type','Availability_Status']

# ── MASTHEAD ──────────────────────────────────────────────
st.markdown(f"""
<div class="masthead">
    <div>
        <span class="brand-name">PropIntel</span>
        <span class="brand-tag">India · 2026</span>
    </div>
    <div class="masthead-stats">
        <div><div class="mstat-val">{len(df):,}</div><div class="mstat-lbl">Properties</div></div>
        <div><div class="mstat-val">{df['City'].nunique()}</div><div class="mstat-lbl">Cities</div></div>
        <div><div class="mstat-val">₹{df['Price_in_Lakhs'].mean():.0f}L</div><div class="mstat-lbl">Avg Price</div></div>
        <div><div class="mstat-val">{df['Good_Investment'].mean()*100:.1f}%</div><div class="mstat-lbl">Good Investments</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI STRIP ─────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
kpis = [
    (k1,"🏘️",f"{len(df):,}",           "Total Properties",  "▲ 5.2%", True),
    (k2,"💰",f"₹{df['Price_in_Lakhs'].mean():.0f}L", "Avg Price", "▲ 3.1%", True),
    (k3,"✅",f"{df['Good_Investment'].mean()*100:.1f}%","Good Investments","▲ 2.4%",True),
    (k4,"📐",f"{df['Size_in_SqFt'].mean():.0f} ft²","Avg Size","▼ 0.8%",False),
    (k5,"🏙️",f"{df['City'].nunique()}",  "Cities Covered",   "▲ 10%",  True),
    (k6,"⚡",f"{df['Infrastructure_Score'].mean():.1f}/7.7","Avg Infra Score","▲ 1.5%",True),
]
for col,icon,val,lbl,delta,up in kpis:
    dc = "up" if up else "down"
    col.markdown(f"""<div class="kpi">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-num">{val}</div>
        <div class="kpi-lbl">{lbl}</div>
        <div class="kpi-delta {dc}">{delta} vs last month</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "01 · Market Overview",
    "02 · Predict Investment",
    "03 · City Intelligence",
    "04 · Deep Analytics"
])

# ════════════════════════════════════════════════════════════
# TAB 1 — MARKET OVERVIEW
# ════════════════════════════════════════════════════════════
with tab1:

    sel_state = st.selectbox("Filter by State",
        ['All States'] + sorted(df['State'].unique().tolist()), key='ov_state')
    fdf = df if sel_state == 'All States' else df[df['State'] == sel_state]

    st.markdown('<div class="sec-label">Market Distribution</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 2, 2])

    with c1:
        st.markdown('<div class="panel"><div class="panel-title">Price Distribution (Lakhs)</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.hist(fdf['Price_in_Lakhs'], bins=60, color=AMBER, edgecolor=BG, alpha=0.9)
        ax.axvline(fdf['Price_in_Lakhs'].mean(), color=WHITE, linestyle='--', linewidth=1.2,
                   label=f"Mean ₹{fdf['Price_in_Lakhs'].mean():.0f}L")
        ax.axvline(fdf['Price_in_Lakhs'].median(), color=GREEN, linestyle='--', linewidth=1.2,
                   label=f"Median ₹{fdf['Price_in_Lakhs'].median():.0f}L")
        ax.legend(fontsize=9, framealpha=0)
        ax.set_xlabel("Price in Lakhs")
        ax.grid(True, axis='y', alpha=0.3)
        fig.patch.set_facecolor(BG); fig.tight_layout()
        st.pyplot(fig); plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel"><div class="panel-title">Investment Quality</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(4, 3.5), subplot_kw=dict(aspect='equal'))
        sizes = fdf['Good_Investment'].value_counts()
        wedges, texts, autotexts = ax.pie(
            sizes, colors=[GREEN, RED], autopct='%1.1f%%', startangle=90,
            wedgeprops={'edgecolor': BG, 'linewidth': 3}, pctdistance=0.75)
        for at in autotexts: at.set_fontsize(11); at.set_fontweight('bold'); at.set_color(WHITE)
        centre = plt.Circle((0,0), 0.55, fc=BG)
        ax.add_artist(centre)
        ax.text(0, 0.1, f"{fdf['Good_Investment'].mean()*100:.1f}%",
                ha='center', va='center', fontsize=20, fontweight='bold', color=GREEN)
        ax.text(0, -0.18, "GOOD", ha='center', va='center', fontsize=9, color=MUTED)
        fig.patch.set_facecolor(BG); fig.tight_layout()
        st.pyplot(fig); plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="panel"><div class="panel-title">BHK Mix</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(4, 3.5))
        bc = fdf['BHK'].value_counts().sort_index()
        ax.barh([f"{b} BHK" for b in bc.index], bc.values,
                color=PALETTE[:len(bc)], height=0.55, edgecolor=BG)
        ax.grid(True, axis='x', alpha=0.3)
        fig.patch.set_facecolor(BG); fig.tight_layout()
        st.pyplot(fig); plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

    # Price Trend by Year Built
    st.markdown('<div class="sec-label">Price Trends Over Time</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Avg Price Trend by Year Built</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(14, 3.8))
    yr_price = fdf.groupby('Year_Built')['Price_in_Lakhs'].mean()
    ax.fill_between(yr_price.index, yr_price.values, alpha=0.1, color=AMBER)
    ax.plot(yr_price.index, yr_price.values, color=AMBER, linewidth=2)
    ax.scatter(yr_price.index, yr_price.values, color=AMBER, s=20, zorder=4)
    ax.set_xlabel("Year Built"); ax.set_ylabel("Avg Price (L)")
    ax.grid(True, axis='y', alpha=0.3)
    fig.patch.set_facecolor(BG); fig.tight_layout()
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

    # Top cities
    st.markdown('<div class="sec-label">City Ranking</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Top 15 Cities — Avg Price in Lakhs</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(14, 3.8))
    city_p = fdf.groupby('City')['Price_in_Lakhs'].mean().sort_values(ascending=False).head(15)
    clrs = [AMBER if p == city_p.max() else '#1c1c22' for p in city_p.values]
    bars = ax.bar(city_p.index, city_p.values, color=clrs, edgecolor=BORDER, width=0.65)
    ax.bar_label(bars, fmt='₹%.0f', padding=3, color=WHITE, fontsize=8.5)
    ax.set_xticklabels(city_p.index, rotation=30, ha='right', fontsize=9)
    ax.set_ylabel("Avg Price (L)"); ax.grid(True, axis='y', alpha=0.3)
    fig.patch.set_facecolor(BG); fig.tight_layout()
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — PREDICT INVESTMENT
# ════════════════════════════════════════════════════════════
with tab2:

    st.markdown('<div class="sec-label">Property Input · AI Analysis</div>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        state      = st.selectbox("State",            sorted(df['State'].unique()))
        city_p     = st.selectbox("City",             sorted(df['City'].unique()))
        locality   = st.selectbox("Locality",         sorted(df['Locality'].unique()))
        prop_type  = st.selectbox("Property Type",    sorted(df['Property_Type'].unique()))
        furnished  = st.selectbox("Furnished Status", sorted(df['Furnished_Status'].unique()))
        avail      = st.selectbox("Availability",     sorted(df['Availability_Status'].unique()))
        owner_type = st.selectbox("Owner Type",       sorted(df['Owner_Type'].unique()))
        facing     = st.selectbox("Facing",           sorted(df['Facing'].unique()))
        transport  = st.selectbox("Public Transport", ['Low','Medium','High'])

    with right:
        bhk          = st.slider("BHK",              1, 5, 3)
        size         = st.slider("Size (SqFt)",      500, 5000, 1500, step=50)
        price        = st.slider("Price (₹ Lakhs)",  10, 500, 100, step=5)
        floor_no     = st.slider("Floor Number",     0, 30, 5)
        total_floors = st.slider("Total Floors",     1, 30, 10)
        year_built   = st.slider("Year Built",       1980, 2024, 2010)
        schools      = st.slider("Nearby Schools",   1, 10, 5)
        hospitals    = st.slider("Nearby Hospitals", 1, 10, 5)
        amenities    = st.slider("Amenities Count",  1, 5, 3)
        pc, sc_ = st.columns(2)
        parking  = pc.selectbox("Parking",  ['Yes','No'])
        security = sc_.selectbox("Security", ['Yes','No'])

    predict_btn = st.button("⚡  RUN AI ANALYSIS", use_container_width=True)

    if predict_btn:
        cy   = datetime.datetime.now().year
        ppsf = (price * 100000) / size
        sd   = schools / (hospitals + 1)
        ts   = {'Low':1,'Medium':2,'High':3}[transport]
        infra= (schools + hospitals + ts) / 3
        fr   = floor_no / (total_floors + 1)
        page = cy - year_built

        def enc_val(col, val):
            try: return int(encoders[col].transform([val])[0])
            except: return 0

        inp = pd.DataFrame([[
            bhk, size, price, ppsf, floor_no, total_floors, fr, page,
            schools, hospitals, ts, infra, amenities, sd,
            enc_val('State',state), enc_val('City',city_p),
            enc_val('Property_Type',prop_type), enc_val('Furnished_Status',furnished),
            enc_val('Facing',facing), enc_val('Owner_Type',owner_type),
            enc_val('Availability_Status',avail)
        ]], columns=FEATURES)

        invest      = clf.predict(inp)[0]
        proba       = clf.predict_proba(inp)[0]
        conf        = proba[invest] * 100
        conf_good   = proba[1] * 100
        conf_bad    = proba[0] * 100
        future_p    = reg.predict(inp)[0]
        profit      = future_p - price
        roi         = (profit / price) * 100

        # ── SECTION A: CLASSIFICATION RESULT ─────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-label">A · Classification — Is This a Good Investment?</div>',
                    unsafe_allow_html=True)

        clf_col, conf_col = st.columns([2, 3])

        with clf_col:
            if invest == 1:
                st.markdown(f"""<div class="clf-good">
                    <span class="clf-icon">✅</span>
                    <div class="clf-title">Good Investment</div>
                    <div class="clf-sub">Model predicts this property<br>is worth buying</div>
                    <div class="clf-conf" style="color:#34d399">{conf:.1f}% Confidence</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="clf-bad">
                    <span class="clf-icon">❌</span>
                    <div class="clf-title">Not Recommended</div>
                    <div class="clf-sub">Model predicts this property<br>is not a good investment</div>
                    <div class="clf-conf" style="color:#f87171">{conf:.1f}% Confidence</div>
                </div>""", unsafe_allow_html=True)

        with conf_col:
            st.markdown('<div class="panel"><div class="panel-title">Model Confidence Score Breakdown</div>',
                        unsafe_allow_html=True)

            # Confidence bars
            st.markdown(f"""
            <div style="margin-bottom:16px">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                    <span style="font-size:12px;color:#34d399;font-weight:700">✅ Good Investment</span>
                    <span style="font-family:'IBM Plex Mono',monospace;color:#34d399;font-weight:700">{conf_good:.1f}%</span>
                </div>
                <div class="conf-bar-bg">
                    <div class="conf-bar-fill" style="width:{conf_good}%;background:linear-gradient(90deg,#34d399,#059669)"></div>
                </div>
            </div>
            <div>
                <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                    <span style="font-size:12px;color:#f87171;font-weight:700">❌ Not Good Investment</span>
                    <span style="font-family:'IBM Plex Mono',monospace;color:#f87171;font-weight:700">{conf_bad:.1f}%</span>
                </div>
                <div class="conf-bar-bg">
                    <div class="conf-bar-fill" style="width:{conf_bad}%;background:linear-gradient(90deg,#f87171,#dc2626)"></div>
                </div>
            </div>
            <br>
            <div style="font-size:11px;color:#6b6b7a;font-family:'IBM Plex Mono',monospace;">
                Model: Random Forest Classifier<br>
                Decision threshold: 50% · Higher = more certain
            </div>
            """, unsafe_allow_html=True)

            # Confidence gauge chart
            fig, ax = plt.subplots(figsize=(6, 2.5))
            ax.barh(['Not Good ❌', 'Good ✅'], [conf_bad, conf_good],
                    color=[RED, GREEN], edgecolor=BG, height=0.4)
            ax.axvline(50, color=WHITE, linestyle='--', linewidth=1, alpha=0.5, label='50% threshold')
            for i, v in enumerate([conf_bad, conf_good]):
                ax.text(v + 1, i, f'{v:.1f}%', va='center', color=WHITE, fontsize=11, fontweight='bold')
            ax.set_xlim(0, 105)
            ax.set_xlabel("Confidence %")
            ax.legend(fontsize=8, framealpha=0)
            ax.grid(True, axis='x', alpha=0.3)
            fig.patch.set_facecolor(BG); fig.tight_layout()
            st.pyplot(fig); plt.close()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── SECTION B: REGRESSION RESULT ─────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-label">B · Regression — Estimated Price After 5 Years</div>',
                    unsafe_allow_html=True)

        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(f"""<div class="reg-card">
                <div class="reg-title">Estimated Price (5yr)</div>
                <div class="reg-val">₹{future_p:.1f}L</div>
                <div class="reg-sub">XGBoost Regressor prediction</div>
            </div>""", unsafe_allow_html=True)
        with r2:
            st.markdown(f"""<div class="stat-pill">
                <div class="pill-val" style="color:#34d399">₹{profit:.1f}L</div>
                <div class="pill-lbl">Expected Profit</div>
            </div>""", unsafe_allow_html=True)
        with r3:
            st.markdown(f"""<div class="stat-pill">
                <div class="pill-val" style="color:#60a5fa">{roi:.1f}%</div>
                <div class="pill-lbl">ROI over 5 Years</div>
            </div>""", unsafe_allow_html=True)
        with r4:
            st.markdown(f"""<div class="stat-pill">
                <div class="pill-val" style="color:#a78bfa">₹{ppsf:,.0f}</div>
                <div class="pill-lbl">Price per SqFt</div>
            </div>""", unsafe_allow_html=True)

        # Price growth projection chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="panel-title">5-Year Price Growth Projection (8% Annual Appreciation)</div>',
                    unsafe_allow_html=True)
        years  = list(range(0, 6))
        prices = [price * (1.08**y) for y in years]
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.fill_between(years, prices, alpha=0.1, color=AMBER)
        ax.plot(years, prices, color=AMBER, linewidth=2.5, zorder=3)
        ax.scatter(years, prices, color=AMBER, s=80, zorder=4, edgecolors=BG, linewidths=2)
        for y, p in zip(years, prices):
            ax.annotate(f'₹{p:.0f}L', (y, p), textcoords="offset points",
                        xytext=(0, 14), ha='center', fontsize=10, color=WHITE, fontweight='bold')
        ax.set_xticks(years)
        ax.set_xticklabels([f'Year {y}' for y in years])
        ax.set_ylabel("Price (Lakhs)")
        ax.grid(True, axis='y', alpha=0.3)
        fig.patch.set_facecolor(BG); fig.tight_layout()
        st.pyplot(fig); plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── SECTION C: FEATURE IMPORTANCE ────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-label">C · Feature Importance — What Drives the Prediction?</div>',
                    unsafe_allow_html=True)

        fi_col1, fi_col2 = st.columns(2)

        with fi_col1:
            st.markdown('<div class="panel"><div class="panel-title">Classification Model — Random Forest Feature Importance</div>',
                        unsafe_allow_html=True)
            feat_imp_clf = pd.Series(clf.feature_importances_, index=FEATURES).sort_values(ascending=True).tail(12)
            fig, ax = plt.subplots(figsize=(7, 5))
            colors_fi = [AMBER if v == feat_imp_clf.max() else BLUE for v in feat_imp_clf.values]
            bars = ax.barh(feat_imp_clf.index, feat_imp_clf.values, color=colors_fi, edgecolor=BG, height=0.6)
            ax.bar_label(bars, fmt='%.3f', padding=3, color=WHITE, fontsize=9)
            ax.set_xlabel("Importance Score")
            ax.set_title("Top 12 Features · Classification", color=WHITE, fontsize=11, fontweight='bold')
            ax.grid(True, axis='x', alpha=0.3)
            fig.patch.set_facecolor(BG); fig.tight_layout()
            st.pyplot(fig); plt.close()
            st.markdown('</div>', unsafe_allow_html=True)

        with fi_col2:
            st.markdown('<div class="panel"><div class="panel-title">Regression Model — XGBoost Feature Importance</div>',
                        unsafe_allow_html=True)
            feat_imp_reg = pd.Series(reg.feature_importances_, index=FEATURES).sort_values(ascending=True).tail(12)
            fig, ax = plt.subplots(figsize=(7, 5))
            colors_fi2 = [AMBER if v == feat_imp_reg.max() else GREEN for v in feat_imp_reg.values]
            bars = ax.barh(feat_imp_reg.index, feat_imp_reg.values, color=colors_fi2, edgecolor=BG, height=0.6)
            ax.bar_label(bars, fmt='%.3f', padding=3, color=WHITE, fontsize=9)
            ax.set_xlabel("Importance Score")
            ax.set_title("Top 12 Features · Regression", color=WHITE, fontsize=11, fontweight='bold')
            ax.grid(True, axis='x', alpha=0.3)
            fig.patch.set_facecolor(BG); fig.tight_layout()
            st.pyplot(fig); plt.close()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── SECTION D: RADAR CHART ────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-label">D · Property Profile Radar</div>', unsafe_allow_html=True)

        rad_col, score_col = st.columns([2, 3])
        with rad_col:
            st.markdown('<div class="panel"><div class="panel-title">Property Radar Chart</div>',
                        unsafe_allow_html=True)
            cats = ['BHK','Infra','Schools','Hospitals','Amenities','Floor']
            vals = [bhk/5, infra/7.7, schools/10, hospitals/10, amenities/5, fr]
            vals += vals[:1]
            N    = len(cats)
            ang  = [n/float(N)*2*np.pi for n in range(N)] + [0]
            fig2, ax2 = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
            fig2.patch.set_facecolor(BG)
            ax2.set_facecolor(BG)
            ax2.plot(ang, vals, color=AMBER, linewidth=2)
            ax2.fill(ang, vals, color=AMBER, alpha=0.2)
            ax2.set_xticks(ang[:-1])
            ax2.set_xticklabels(cats, color=MUTED, size=10)
            ax2.set_ylim(0, 1)
            ax2.yaxis.set_visible(False)
            ax2.spines['polar'].set_color(BORDER)
            ax2.grid(color=BORDER, linewidth=0.8)
            fig2.tight_layout()
            st.pyplot(fig2); plt.close()
            st.markdown('</div>', unsafe_allow_html=True)

        with score_col:
            st.markdown('<div class="panel"><div class="panel-title">Property Score Breakdown</div>',
                        unsafe_allow_html=True)
            s1,s2,s3 = st.columns(3)
            s4,s5,s6 = st.columns(3)
            scores = [
                (s1,"Infra Score",    f"{infra:.2f}/7.7",  GREEN),
                (s2,"School Density", f"{sd:.2f}",          AMBER),
                (s3,"Floor Ratio",    f"{fr:.2f}",           BLUE),
                (s4,"Property Age",   f"{page} yrs",        '#fb923c'),
                (s5,"Amenities",      f"{amenities}/5",     PURPLE),
                (s6,"Transport",      transport,             '#38bdf8'),
            ]
            for col, lbl, val, clr in scores:
                col.markdown(f"""<div class="stat-pill">
                    <div class="pill-val" style="color:{clr}">{val}</div>
                    <div class="pill-lbl">{lbl}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — CITY INTELLIGENCE
# ════════════════════════════════════════════════════════════
with tab3:
    with tab3:

        st.markdown('<div class="sec-label">Location-wise Heatmaps & City Analysis</div>',
                    unsafe_allow_html=True)

        c_state = st.selectbox("Filter by State",
                               ['All States'] + sorted(df['State'].unique().tolist()),
                               key='city_tab')
        cdf = df if c_state == 'All States' else df[df['State'] == c_state]

        # ── HEATMAP 1: State vs BHK — Avg Price ──────────────
        st.markdown('<div class="panel"><div class="panel-title">🔥 Heatmap 1 · State vs BHK — Avg Price (Lakhs)</div>',
                    unsafe_allow_html=True)
        state_bhk = df.groupby(['State', 'BHK'])['Price_in_Lakhs'].mean().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(state_bhk, annot=True, fmt='.0f', cmap='YlOrRd',
                    ax=ax, linewidths=0.5, linecolor=BG,
                    annot_kws={'size': 9}, cbar_kws={'shrink': 0.8})
        ax.set_title("Avg Price (Lakhs) — State vs BHK", color=WHITE, fontsize=13, fontweight='bold')
        ax.set_xlabel("BHK", color=MUTED)
        ax.set_ylabel("State", color=MUTED)
        ax.tick_params(axis='x', colors=WHITE, labelsize=10)
        ax.tick_params(axis='y', colors=WHITE, labelsize=9)
        fig.patch.set_facecolor(BG);
        fig.tight_layout()
        st.pyplot(fig);
        plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── HEATMAP 2: State vs Property Type — Avg Price ────
        st.markdown(
            '<div class="panel"><div class="panel-title">🔥 Heatmap 2 · State vs Property Type — Avg Price (Lakhs)</div>',
            unsafe_allow_html=True)
        state_type = df.groupby(['State', 'Property_Type'])['Price_in_Lakhs'].mean().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(state_type, annot=True, fmt='.0f', cmap='Blues',
                    ax=ax, linewidths=0.5, linecolor=BG,
                    annot_kws={'size': 9}, cbar_kws={'shrink': 0.8})
        ax.set_title("Avg Price (Lakhs) — State vs Property Type", color=WHITE, fontsize=13, fontweight='bold')
        ax.set_xlabel("Property Type", color=MUTED)
        ax.set_ylabel("State", color=MUTED)
        ax.tick_params(axis='x', colors=WHITE, labelsize=10, rotation=20)
        ax.tick_params(axis='y', colors=WHITE, labelsize=9)
        fig.patch.set_facecolor(BG);
        fig.tight_layout()
        st.pyplot(fig);
        plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── HEATMAP 3: State vs Good Investment % ────────────
        st.markdown('<div class="panel"><div class="panel-title">🔥 Heatmap 3 · State vs BHK — Good Investment % </div>',
                    unsafe_allow_html=True)
        state_inv = df.groupby(['State', 'BHK'])['Good_Investment'].mean().unstack(fill_value=0) * 100
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(state_inv, annot=True, fmt='.1f', cmap='Greens',
                    ax=ax, linewidths=0.5, linecolor=BG,
                    annot_kws={'size': 9}, cbar_kws={'shrink': 0.8})
        ax.set_title("Good Investment % — State vs BHK", color=WHITE, fontsize=13, fontweight='bold')
        ax.set_xlabel("BHK", color=MUTED)
        ax.set_ylabel("State", color=MUTED)
        ax.tick_params(axis='x', colors=WHITE, labelsize=10)
        ax.tick_params(axis='y', colors=WHITE, labelsize=9)
        fig.patch.set_facecolor(BG);
        fig.tight_layout()
        st.pyplot(fig);
        plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── HEATMAP 4: City vs Property Type — Avg Price ─────
        st.markdown(
            '<div class="panel"><div class="panel-title">🔥 Heatmap 4 · City vs Property Type — Avg Price (Lakhs)</div>',
            unsafe_allow_html=True)
        top_cities_heat = cdf['City'].value_counts().head(12).index
        heat_df = cdf[cdf['City'].isin(top_cities_heat)].groupby(
            ['City', 'Property_Type'])['Price_in_Lakhs'].mean().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(14, 5))
        sns.heatmap(heat_df, annot=True, fmt='.0f', cmap='YlOrBr',
                    ax=ax, linewidths=0.4, linecolor=BG,
                    annot_kws={'size': 9}, cbar_kws={'shrink': 0.8})
        ax.set_title("Avg Price (Lakhs) — City vs Property Type", color=WHITE, fontsize=13, fontweight='bold')
        ax.set_xlabel("Property Type", color=MUTED)
        ax.set_ylabel("City", color=MUTED)
        ax.tick_params(axis='x', colors=WHITE, labelsize=9, rotation=20)
        ax.tick_params(axis='y', colors=WHITE, labelsize=9)
        fig.patch.set_facecolor(BG);
        fig.tight_layout()
        st.pyplot(fig);
        plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── HEATMAP 5: City vs BHK — Infrastructure Score ────
        st.markdown(
            '<div class="panel"><div class="panel-title">🔥 Heatmap 5 · City vs BHK — Infrastructure Score</div>',
            unsafe_allow_html=True)
        infra_heat = cdf[cdf['City'].isin(top_cities_heat)].groupby(
            ['City', 'BHK'])['Infrastructure_Score'].mean().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(14, 5))
        sns.heatmap(infra_heat, annot=True, fmt='.1f', cmap='PuBu',
                    ax=ax, linewidths=0.4, linecolor=BG,
                    annot_kws={'size': 10}, cbar_kws={'shrink': 0.8})
        ax.set_title("Avg Infrastructure Score — City vs BHK", color=WHITE, fontsize=13, fontweight='bold')
        ax.set_xlabel("BHK", color=MUTED)
        ax.set_ylabel("City", color=MUTED)
        ax.tick_params(axis='x', colors=WHITE, labelsize=10)
        ax.tick_params(axis='y', colors=WHITE, labelsize=9)
        fig.patch.set_facecolor(BG);
        fig.tight_layout()
        st.pyplot(fig);
        plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── HEATMAP 6: Furnished Status vs Transport — Price ─
        st.markdown(
            '<div class="panel"><div class="panel-title">🔥 Heatmap 6 · Furnished Status vs Public Transport — Avg Price</div>',
            unsafe_allow_html=True)
        furn_trans = df.groupby(
            ['Furnished_Status', 'Public_Transport_Accessibility'])['Price_in_Lakhs'].mean().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(furn_trans, annot=True, fmt='.0f', cmap='OrRd',
                    ax=ax, linewidths=0.5, linecolor=BG,
                    annot_kws={'size': 11}, cbar_kws={'shrink': 0.8})
        ax.set_title("Avg Price — Furnished Status vs Transport", color=WHITE, fontsize=13, fontweight='bold')
        ax.set_xlabel("Public Transport Accessibility", color=MUTED)
        ax.set_ylabel("Furnished Status", color=MUTED)
        ax.tick_params(axis='x', colors=WHITE, labelsize=10)
        ax.tick_params(axis='y', colors=WHITE, labelsize=10, rotation=0)
        fig.patch.set_facecolor(BG);
        fig.tight_layout()
        st.pyplot(fig);
        plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── CITY CHARTS ───────────────────────────────────────
        st.markdown('<div class="sec-label">City Rankings</div>', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)

        with cc1:
            st.markdown('<div class="panel"><div class="panel-title">Top Cities · Avg Price (Lakhs)</div>',
                        unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(7, 5))
            cp2 = cdf.groupby('City')['Price_in_Lakhs'].mean().sort_values(ascending=True).tail(12)
            clrs = [AMBER if p == cp2.max() else '#1c1c22' for p in cp2.values]
            bars = ax.barh(cp2.index, cp2.values, color=clrs, height=0.6, edgecolor=BG)
            ax.bar_label(bars, fmt='₹%.0fL', padding=4, color=WHITE, fontsize=9)
            ax.set_xlabel("Avg Price (L)")
            ax.grid(True, axis='x', alpha=0.3)
            fig.patch.set_facecolor(BG);
            fig.tight_layout()
            st.pyplot(fig);
            plt.close()
            st.markdown('</div>', unsafe_allow_html=True)

        with cc2:
            st.markdown('<div class="panel"><div class="panel-title">Best Investment Cities (%)</div>',
                        unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(7, 5))
            ci2 = cdf.groupby('City')['Good_Investment'].mean().sort_values(ascending=True).tail(12) * 100
            clrs2 = [GREEN if p == ci2.max() else '#1c1c22' for p in ci2.values]
            bars = ax.barh(ci2.index, ci2.values, color=clrs2, height=0.6, edgecolor=BG)
            ax.bar_label(bars, fmt='%.1f%%', padding=4, color=WHITE, fontsize=9)
            ax.set_xlabel("Good Investment %")
            ax.grid(True, axis='x', alpha=0.3)
            fig.patch.set_facecolor(BG);
            fig.tight_layout()
            st.pyplot(fig);
            plt.close()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── CITY DEEP DIVE ────────────────────────────────────
        st.markdown('<div class="sec-label">City Deep Dive</div>', unsafe_allow_html=True)
        city_dd = st.selectbox("Select City", sorted(cdf['City'].unique()), key='dd_city')
        ddf = cdf[cdf['City'] == city_dd]

        d1, d2, d3, d4, d5 = st.columns(5)
        deep = [
            (d1, "Avg Price", f"₹{ddf['Price_in_Lakhs'].mean():.1f}L", AMBER),
            (d2, "Properties", f"{len(ddf):,}", WHITE),
            (d3, "Good Investment", f"{ddf['Good_Investment'].mean() * 100:.1f}%", GREEN),
            (d4, "Avg SqFt", f"{ddf['Size_in_SqFt'].mean():.0f}", BLUE),
            (d5, "Avg Infra Score", f"{ddf['Infrastructure_Score'].mean():.2f}", PURPLE),
        ]
        for col, lbl, val, clr in deep:
            col.markdown(f"""<div class="stat-pill">
                <div class="pill-val" style="color:{clr}">{val}</div>
                <div class="pill-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))

        bc = ddf['BHK'].value_counts().sort_index()
        axes[0].bar([f"{b}BHK" for b in bc.index], bc.values,
                    color=PALETTE[:len(bc)], edgecolor=BG)
        axes[0].set_title(f"BHK Mix · {city_dd}", color=WHITE, fontsize=11, fontweight='bold')
        axes[0].grid(True, axis='y', alpha=0.3)
        axes[0].set_facecolor(BG)

        axes[1].hist(ddf['Price_in_Lakhs'], bins=30, color=AMBER, edgecolor=BG, alpha=0.9)
        axes[1].axvline(ddf['Price_in_Lakhs'].mean(), color=WHITE, linestyle='--',
                        linewidth=1.5, label=f"Mean ₹{ddf['Price_in_Lakhs'].mean():.0f}L")
        axes[1].legend(fontsize=9, framealpha=0)
        axes[1].set_title(f"Price Distribution · {city_dd}", color=WHITE, fontsize=11, fontweight='bold')
        axes[1].set_xlabel("Price (L)")
        axes[1].grid(True, axis='y', alpha=0.3)
        axes[1].set_facecolor(BG)

        pt_counts = ddf['Property_Type'].value_counts()
        wedges, texts, autotexts = axes[2].pie(
            pt_counts.values, labels=pt_counts.index,
            colors=PALETTE[:len(pt_counts)], autopct='%1.0f%%', startangle=90,
            wedgeprops={'edgecolor': BG, 'linewidth': 2},
            textprops={'color': WHITE, 'fontsize': 8}
        )
        for at in autotexts: at.set_fontsize(8)
        axes[2].set_title(f"Property Types · {city_dd}", color=WHITE, fontsize=11, fontweight='bold')
        axes[2].set_facecolor(BG)

        for ax_ in axes: ax_.spines['bottom'].set_color(BORDER)
        fig.patch.set_facecolor(BG);
        fig.tight_layout()
        st.pyplot(fig);
        plt.close()

# ════════════════════════════════════════════════════════════
# TAB 4 — DEEP ANALYTICS
# ════════════════════════════════════════════════════════════
with tab4:

    st.markdown('<div class="sec-label">Deep Analytics · Correlations & Patterns</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">Feature Correlation Matrix</div>',
                unsafe_allow_html=True)
    num_cols = ['Price_in_Lakhs','Size_in_SqFt','BHK','Nearby_Schools',
                'Nearby_Hospitals','Price_per_SqFt_calc','Infrastructure_Score',
                'Amenities_Count','Future_Price_5yr','Good_Investment',
                'Floor_Ratio','Property_Age']
    import numpy as np
    fig, ax = plt.subplots(figsize=(13, 6))
    mask = np.zeros_like(df[num_cols].corr())
    mask[np.triu_indices_from(mask)] = True
    sns.heatmap(df[num_cols].corr(), mask=mask, annot=True, fmt='.2f',
                cmap='RdYlGn', ax=ax, linewidths=0.4, linecolor=BG,
                annot_kws={'size': 8.5}, center=0, cbar_kws={'shrink': 0.8})
    ax.tick_params(colors=WHITE, labelsize=9)
    fig.patch.set_facecolor(BG); fig.tight_layout()
    st.pyplot(fig); plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

    da1, da2 = st.columns([2, 3])
    with da1:
        st.markdown('<div class="panel"><div class="panel-title">Price by Furnished Status</div>',
                    unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5.5, 4))
        furn_types = df['Furnished_Status'].unique()
        data_ = [df[df['Furnished_Status']==f]['Price_in_Lakhs'].values for f in furn_types]
        bp = ax.boxplot(data_, patch_artist=True,
                        medianprops={'color': WHITE, 'linewidth': 2},
                        whiskerprops={'color': BORDER},
                        capprops={'color': BORDER},
                        flierprops={'marker':'o','markersize':2,'markerfacecolor':AMBER,'alpha':0.3})
        for patch, color in zip(bp['boxes'], PALETTE):
            patch.set_facecolor(color); patch.set_alpha(0.7)
        ax.set_xticklabels(furn_types, rotation=20, ha='right', fontsize=9)
        ax.set_ylabel("Price (Lakhs)")
        ax.grid(True, axis='y', alpha=0.3)
        fig.patch.set_facecolor(BG); fig.tight_layout()
        st.pyplot(fig); plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

    with da2:
        st.markdown('<div class="panel"><div class="panel-title">Infrastructure Score vs Price · Good vs Not Good Investment</div>',
                    unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(7.5, 4))
        sample2 = df.sample(min(5000, len(df)), random_state=7)
        good_ = sample2[sample2['Good_Investment'] == 1]
        bad_  = sample2[sample2['Good_Investment'] == 0]
        ax.scatter(bad_['Infrastructure_Score'],  bad_['Price_in_Lakhs'],
                   color=RED,   alpha=0.4, s=8, label='Not Good Investment', rasterized=True)
        ax.scatter(good_['Infrastructure_Score'], good_['Price_in_Lakhs'],
                   color=GREEN, alpha=0.5, s=8, label='Good Investment', rasterized=True)
        ax.legend(fontsize=9, framealpha=0.3, facecolor='#1c1c22', labelcolor=WHITE)
        ax.set_xlabel("Infrastructure Score")
        ax.set_ylabel("Price (Lakhs)")
        ax.grid(True, alpha=0.2)
        fig.patch.set_facecolor(BG); fig.tight_layout()
        st.pyplot(fig); plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:30px 0 10px 0;
     font-family:"IBM Plex Mono",monospace;
     font-size:10px;color:#2a2a35;
     letter-spacing:3px;text-transform:uppercase;'>
    PropIntel · India Real Estate Intelligence · 2026
</div>
""", unsafe_allow_html=True)