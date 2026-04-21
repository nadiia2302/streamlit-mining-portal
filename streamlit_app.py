import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
from fpdf import FPDF
import io

# --- 1. Page Configuration ---
st.set_page_config(page_title="Weyland-Yutani Analytics", layout="wide")
st.title("📊 Weyland-Yutani Multi-Mine Analytics Portal")

# --- 2. Google Sheets Connection ---
conn = st.connection("gsheets", type=GSheetsConnection)

# List of your mines (ensure these exact names exist as tabs in your Google Sheet)
MINE_LIST = ["LV-426", "Fiorina 151", "Origae-6"]

@st.cache_data(ttl=600)
def load_data(worksheet_name):
    # Load worksheet
    df = conn.read(worksheet=worksheet_name, usecols=list(range(8)), ttl=5)
    df = df.dropna(how="all")
    
    # Clean Date column (assuming it's the second column)
    df.rename(columns={df.columns[1]: 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
    df = df.sort_values(by='Date')
    
    # Convert all other columns to numeric
    numeric_cols = [c for c in df.columns if c != 'Date']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

# --- 3. Mathematical Functions ---
def grubbs_test(x):
    n = len(x)
    mean_x = np.mean(x)
    std_x = np.std(x)
    if std_x == 0 or n < 3: return np.zeros(n, dtype=bool)
    G = np.abs(x - mean_x) / std_x
    t_dist = stats.t.ppf(1 - 0.05 / (2 * n), n - 2)
    G_critical = ((n - 1) / np.sqrt(n)) * np.sqrt(t_dist**2 / (n - 2 + t_dist**2))
    return G > G_critical

# --- 4. Sidebar Controls ---
st.sidebar.header("Global Settings")
selected_mine = st.sidebar.selectbox("Select Mine Location", MINE_LIST)

# Load data based on selected mine
df = load_data(selected_mine)
numeric_cols = [c for c in df.columns if c != 'Date']

st.sidebar.header("Analysis Parameters")
selected_col = st.sidebar.selectbox("Analysis Metric", numeric_cols)
chart_type = st.sidebar.radio("Chart Type", ["Line", "Bar"])
poly_degree = st.sidebar.slider("Trendline Polynomial Degree", 1, 4, 1)

st.sidebar.subheader("Anomaly Detection")
z_thresh = st.sidebar.slider("Z-Score Threshold", 1.0, 3.0, 2.0)
ma_window = st.sidebar.slider("MA Window Size", 2, 10, 5)
ma_percent = st.sidebar.slider("MA Distance Threshold (%)", 5, 50, 20)

# --- 5. Data Analytics ---
x_values = df[selected_col].fillna(0).values

# Detect Anomalies (Composite)
z_scores = np.abs(stats.zscore(x_values))
ma = df[selected_col].rolling(window=ma_window).mean()
ma_dist = np.abs(df[selected_col] - ma) / ma

outliers_mask = (z_scores > z_thresh) | (ma_dist > (ma_percent / 100)) | grubbs_test(x_values)
outliers = df[outliers_mask]

# Stats
mean_val = df[selected_col].mean()
median_val = df[selected_col].median()
std_val = df[selected_col].std()
iqr_val = df[selected_col].quantile(0.75) - df[selected_col].quantile(0.25)

# --- 6. Metrics and Chart ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Mean", f"{mean_val:.2f}")
col2.metric("Median", f"{median_val:.2f}")
col3.metric("Std Dev", f"{std_val:.2f}")
col4.metric("IQR", f"{iqr_val:.2f}")

fig = go.Figure()

# Plot Data
if chart_type == "Line":
    fig.add_trace(go.Scatter(x=df['Date'], y=df[selected_col], mode='lines', name=selected_col))
else:
    fig.add_trace(go.Bar(x=df['Date'], y=df[selected_col], name=selected_col))

# Trendline
x_idx = np.arange(len(df))
z = np.polyfit(x_idx, df[selected_col].fillna(0), poly_degree)
p = np.poly1d(z)
fig.add_trace(go.Scatter(x=df['Date'], y=p(x_idx), mode='lines', name='Trend', line=dict(dash='dash', color='green')))

# Anomalies
fig.add_trace(go.Scatter(x=outliers['Date'], y=outliers[selected_col], mode='markers', 
                         name='Anomalies', marker=dict(color='red', size=10)))

st.plotly_chart(fig, use_container_width=True)

# --- 7. PDF Export ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Weyland-Yutani Report: {selected_mine}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Metric Analyzed: {selected_col}", ln=True)
    pdf.cell(200, 10, txt=f"Mean: {mean_val:.2f} | Median: {median_val:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Std Dev: {std_val:.2f} | IQR: {iqr_val:.2f}", ln=True)

    
    return pdf.output(dest='S').encode('latin-1')

st.download_button("📥 Download PDF Report", generate_pdf(), f"report_{selected_mine}_{selected_col}.pdf")