import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Secure Power BI Enterprise",
    layout="wide",
    page_icon="📊"
)

# =====================================
# SECURE USER DATABASE
# =====================================
USERS = {
    "admin": {
        "pwd": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "Admin"
    },
    "analyst": {
        "pwd": hashlib.sha256("1234".encode()).hexdigest(),
        "role": "Analyst"
    },
    "viewer": {
        "pwd": hashlib.sha256("viewer".encode()).hexdigest(),
        "role": "Viewer"
    }
}

# =====================================
# AUTHENTICATION
# =====================================
def authenticate(username, password):

    user = USERS.get(username)

    if not user:
        return False, None

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    if hashed_password == user["pwd"]:
        return True, user["role"]

    return False, None


# =====================================
# SESSION STATE
# =====================================
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.reports = {}

# =====================================
# LOGIN SCREEN
# =====================================
if not st.session_state.auth:

    st.title("🔐 Secure Enterprise Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        success, role = authenticate(username, password)

        if success:
            st.session_state.auth = True
            st.session_state.user = username
            st.session_state.role = role
            st.rerun()

        else:
            st.error("❌ Invalid credentials")

    st.stop()

# =====================================
# USER ROLE
# =====================================
role = st.session_state.role

# =====================================
# LOAD DATA
# =====================================
@st.cache_data
def load_data():

    # FIXED:
    # 'M' removed in latest pandas
    # Use 'ME' (Month End)

    months = pd.date_range(
        start="2020-01-01",
        periods=60,
        freq="ME"
    )

    data = []

    for i, month in enumerate(months):

        leads = max(10, 120 + i * 4 + np.random.randint(0, 10))

        conversions = max(
            1,
            int(leads * (0.20 + i * 0.002))
        )

        revenue = leads * 300 + conversions * 1500
        cost = leads * 120

        data.append({
            "Month": month,
            "Year": month.year,
            "Leads": leads,
            "Conversions": conversions,
            "Revenue": revenue,
            "Cost": cost,
            "SEO": min(100, 40 + i),
            "UX": min(100, 30 + i),
            "Product": np.random.choice(
                ["SaaS", "API", "Analytics"]
            ),
            "Market": np.random.choice(
                ["India", "US", "Global"]
            )
        })

    dataframe = pd.DataFrame(data)

    return dataframe


# =====================================
# DATAFRAME
# =====================================
df = load_data()

# =====================================
# FEATURE ENGINEERING
# =====================================
df["ROI"] = np.where(
    df["Cost"] > 0,
    ((df["Revenue"] - df["Cost"]) / df["Cost"]) * 100,
    0
)

df["CAC"] = df["Cost"] / (df["Conversions"] + 1)

df["Risk"] = (
    (100 - df["SEO"]) * 0.5 +
    (100 - df["UX"]) * 0.5
)

df["Efficiency"] = (
    df["Revenue"] / (df["Cost"] + 1)
)

# =====================================
# MACHINE LEARNING MODEL
# =====================================
df["t"] = range(len(df))

X = df[["t", "SEO", "UX"]].fillna(0)
y = df["Revenue"].fillna(0)

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# =====================================
# FUTURE PREDICTION
# =====================================
future = pd.DataFrame({
    "t": range(len(df), len(df) + 24),
    "SEO": np.random.randint(40, 100, 24),
    "UX": np.random.randint(40, 100, 24)
})

future["Prediction"] = model.predict(
    future[["t", "SEO", "UX"]]
)

# =====================================
# SIDEBAR
# =====================================
st.sidebar.title("📊 Enterprise Control Panel")

page = st.sidebar.radio(
    "Navigation",
    [
        "📌 Dashboard",
        "📈 Report Builder",
        "🧠 AI Forecast",
        "📂 Data"
    ]
)

theme = st.sidebar.color_picker(
    "Theme Color",
    "#00A8FF"
)

st.sidebar.markdown(f"""
### 👤 User Information

**User:** {st.session_state.user}

**Role:** {role}
""")

# =====================================
# SAVE REPORT
# =====================================
def save_report(name, config):

    if not name.strip():
        st.error("❌ Report name cannot be empty")
        return

    st.session_state.reports[name] = {
        "user": st.session_state.user,
        "config": config
    }

# =====================================
# DASHBOARD
# =====================================
if page == "📌 Dashboard":

    st.title("📊 Executive Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Revenue",
        f"₹{int(df['Revenue'].sum()):,}"
    )

    col2.metric(
        "Average ROI",
        f"{round(df['ROI'].mean(), 2)}%"
    )

    col3.metric(
        "Efficiency",
        round(df["Efficiency"].mean(), 2)
    )

    col4.metric(
        "Risk Score",
        round(df["Risk"].mean(), 2)
    )

    fig = px.line(
        df,
        x="Month",
        y="Revenue",
        color="Product",
        title="Revenue Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# REPORT BUILDER
# =====================================
elif page == "📈 Report Builder":

    st.title("📈 Secure Report Builder")

    chart_type = st.selectbox(
        "Select Chart Type",
        ["Line", "Bar", "Scatter"]
    )

    x_axis = st.selectbox(
        "Select X Axis",
        df.columns
    )

    y_axis = st.selectbox(
        "Select Y Axis",
        df.columns
    )

    color = st.selectbox(
        "Color By",
        ["Product", "Market", "None"]
    )

    report_name = st.text_input(
        "Enter Report Name"
    )

    selected_color = None if color == "None" else color

    # Generate chart
    if chart_type == "Line":

        fig = px.line(
            df,
            x=x_axis,
            y=y_axis,
            color=selected_color
        )

    elif chart_type == "Bar":

        fig = px.bar(
            df,
            x=x_axis,
            y=y_axis,
            color=selected_color
        )

    else:

        fig = px.scatter(
            df,
            x=x_axis,
            y=y_axis,
            color=selected_color
        )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    if st.button("💾 Save Report"):

        save_report(
            report_name,
            {
                "chart": chart_type,
                "x": x_axis,
                "y": y_axis,
                "color": color
            }
        )

        st.success("✅ Report Saved Successfully")

# =====================================
# AI FORECAST
# =====================================
elif page == "🧠 AI Forecast":

    st.title("🧠 AI Revenue Forecast")

    combined = pd.concat([
        df[["Revenue"]],

        future[["Prediction"]].rename(
            columns={"Prediction": "Revenue"}
        )
    ])

    fig = px.line(
        combined,
        y="Revenue",
        title="Future Revenue Prediction"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# DATA EXPLORER
# =====================================
elif page == "📂 Data":

    st.title("📂 Dataset Explorer")

    st.dataframe(
        df,
        use_container_width=True
    )

# =====================================
# CUSTOM THEME
# =====================================
st.markdown(
    f"""
    <style>
    h1, h2, h3 {{
        color: {theme};
    }}

    .stButton>button {{
        background-color: {theme};
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
