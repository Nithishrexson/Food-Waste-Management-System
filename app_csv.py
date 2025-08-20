# -------------------------
# Imports
# -------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Food Waste Management System", layout="wide")

# -------------------------
# Load CSV files
# -------------------------
@st.cache_data
def load_data():
    providers = pd.read_csv("providers_final.csv")
    receivers = pd.read_csv("receivers_final.csv")
    food_listings = pd.read_csv("food_listings.csv")
    claims = pd.read_csv("claims.csv")
    # Ensure dates are parsed as datetime
    if 'Expiry_Date' in food_listings.columns:
        food_listings['Expiry_Date'] = pd.to_datetime(food_listings['Expiry_Date'], errors='coerce')
    if 'Timestamp' in claims.columns:
        claims['Timestamp'] = pd.to_datetime(claims['Timestamp'], errors='coerce')
    return providers, receivers, food_listings, claims

providers, receivers, food_listings, claims = load_data()

# -------------------------
# Get counts
# -------------------------
def get_count(df):
    return len(df)

# -------------------------
# Define Queries (Global)
# -------------------------
def query_1():  # List all providers
    return providers.head(20)

def query_2():  # Count of providers by city
    return providers.groupby("City").size().reset_index(name="Provider_Count").sort_values("Provider_Count", ascending=False)

def query_3():  # Providers with most listings
    df = food_listings.groupby("Provider_ID").size().reset_index(name="Total_Listings")
    return df.merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values("Total_Listings", ascending=False).head(10)

def query_4():  # Top 5 providers with maximum claims
    merged = food_listings.merge(claims, on="Food_ID", how="left")
    df = merged.groupby("Provider_ID")['Claim_ID'].count().reset_index(name="Total_Claims")
    return df.merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values("Total_Claims", ascending=False).head(5)

def query_5():  # Providers with expired food listings
    today = pd.Timestamp(datetime.today().date())
    expired = food_listings[food_listings['Expiry_Date'] < today]
    df = expired.groupby("Provider_ID").size().reset_index(name="Expired_Listings")
    return df.merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values("Expired_Listings", ascending=False)

def query_6():  # Average food quantity provided per provider
    df = food_listings.groupby("Provider_ID")['Quantity'].mean().reset_index(name="Avg_Quantity")
    return df.merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values("Avg_Quantity", ascending=False)

def query_7():  # Provider with maximum unique receivers
    merged = food_listings.merge(claims, on="Food_ID", how="left")
    df = merged.groupby("Provider_ID")['Receiver_ID'].nunique().reset_index(name="Unique_Receivers")
    return df.merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values("Unique_Receivers", ascending=False).head(1)

def query_8():  # Percentage contribution of each provider to total listings
    total = len(food_listings)
    df = food_listings.groupby("Provider_ID").size().reset_index(name="Listings")
    df['Contribution_Percentage'] = df['Listings']*100.0/total
    return df.merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values("Contribution_Percentage", ascending=False)

def query_9():  # Providers with zero claims
    claimed = claims.merge(food_listings[['Food_ID','Provider_ID']], on="Food_ID", how="right")
    df = claimed.groupby("Provider_ID")['Claim_ID'].count().reset_index(name="Claim_Count")
    zero_claims = df[df['Claim_Count']==0]
    return zero_claims.merge(providers[['Provider_ID','Name']], on="Provider_ID")[['Name']]

def query_10():  # City-wise claim distribution for providers
    merged = food_listings.merge(claims, on="Food_ID", how="left").merge(providers[['Provider_ID','City']], on="Provider_ID")
    return merged.groupby("City")['Claim_ID'].count().reset_index(name="Total_Claims").sort_values("Total_Claims", ascending=False)

def query_11():  # Top providers by completed claims
    merged = food_listings.merge(claims, on="Food_ID", how="left")
    df = merged[merged['Status']=='Completed'].groupby("Provider_ID")['Claim_ID'].count().reset_index(name="Completed_Claims")
    return df.merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values("Completed_Claims", ascending=False).head(5)

def query_12():  # Claim status breakdown per provider
    merged = food_listings.merge(claims, on="Food_ID", how="left")
    df = merged.groupby(['Provider_ID','Status']).size().reset_index(name='Count')
    return df.merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values(['Name','Count'], ascending=[True,False])

provider_queries = {
    "1. List all providers": query_1,
    "2. Count of providers by city": query_2,
    "3. Providers with most listings": query_3,
    "4. Top 5 providers with maximum claims": query_4,
    "5. Providers with expired food listings": query_5,
    "6. Average food quantity provided per provider": query_6,
    "7. Provider with maximum unique receivers": query_7,
    "8. Percentage contribution of each provider to total listings": query_8,
    "9. Providers with zero claims": query_9,
    "10. City-wise claim distribution for providers": query_10,
    "11. Top providers by completed claims": query_11,
    "12. Claim status breakdown per provider": query_12
}

descriptions = {
    "1. List all providers": "Shows a preview of provider data (first 20 rows).",
    "2. Count of providers by city": "Number of providers in each city.",
    "3. Providers with most listings": "Top providers ranked by total food listings.",
    "4. Top 5 providers with maximum claims": "Shows which providers have the most claims.",
    "5. Providers with expired food listings": "Lists providers whose food has expired.",
    "6. Average food quantity provided per provider": "Average food quantity listed per provider.",
    "7. Provider with maximum unique receivers": "Which provider serves the most unique receivers.",
    "8. Percentage contribution of each provider to total listings": "Share of total listings per provider.",
    "9. Providers with zero claims": "Providers whose listings were never claimed.",
    "10. City-wise claim distribution for providers": "How claims are distributed across cities.",
    "11. Top providers by completed claims": "Top providers ranked by completed claims.",
    "12. Claim status breakdown per provider": "Shows claim status (Completed/Pending) by provider."
}

# -------------------------
# Sidebar Navigation
# -------------------------
menu = st.sidebar.radio("📌 Navigation", ["Project Introduction","Dashboard", "Queries", "Data Visualization","Creator Info"])

# -------------------------
# Centered Title
# -------------------------
st.markdown(
    """
    <div style="background-color:orange; padding:20px; border-radius:12px; text-align:center; margin-bottom:30px;">
        <h1 style="color:white; margin:0;">🍽️ Food Waste Management System</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# KPI Box Style
# -------------------------
def kpi_box(title, value):
    return f"""
        <div style="background-color:orange;
                    padding:20px;
                    border-radius:12px;
                    text-align:center;
                    margin:auto;">
            <h3 style="color:white; font-size:20px;">{title}</h3>
            <h1 style="color:white; font-size:26px;">{value}</h1>
        </div>
    """

# -------------------------
# Project Introduction Page
# -------------------------
if menu == "Project Introduction":
    st.markdown("## 📖 Project Introduction")
    st.markdown("""
    <div style="padding:20px; background-color:#f9f9f9; border-radius:10px;">
        <h2 style="color:#333;">Food Waste Management System</h2>
        <p>This project helps manage surplus food and reduce wastage by connecting providers with those in need.</p>
        <ul style="font-size:16px; line-height:1.8;">
            <li><b>Providers:</b> Restaurants, households, and businesses list surplus food.</li>
            <li><b>Receivers:</b> NGOs and individuals claim available food.</li>
            <li><b>Geolocation:</b> Helps locate nearby food.</li>
            <li><b>CSV Analysis:</b> Powerful insights using pandas queries.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# Dashboard Page
# -------------------------
elif menu == "Dashboard":
    total_providers = get_count(providers)
    total_receivers = get_count(receivers)
    total_listings = get_count(food_listings)
    total_claims = get_count(claims)

    col1, col2, col3, col4, empty = st.columns([2,2,2,2,1])
    with col1: st.markdown(kpi_box("Providers", total_providers), unsafe_allow_html=True)
    with col2: st.markdown(kpi_box("Receivers", total_receivers), unsafe_allow_html=True)
    with col3: st.markdown(kpi_box("Listings", total_listings), unsafe_allow_html=True)
    with col4: st.markdown(kpi_box("Claims", total_claims), unsafe_allow_html=True)

    st.markdown("### 📂 Explore Tables")
    tables = {
        "Providers": providers,
        "Receivers": receivers,
        "Food Listings": food_listings,
        "Claims": claims
    }
    selected_table_name = st.selectbox("Select a table to view:", list(tables.keys()))
    selected_table = tables[selected_table_name]

    if st.button("Generate Table"):
        st.dataframe(selected_table.head(20), use_container_width=True)

# -------------------------
# Queries Page
# -------------------------
elif menu == "Queries":
    total_providers = get_count(providers)
    total_receivers = get_count(receivers)
    total_listings = get_count(food_listings)
    total_claims = get_count(claims)

    col1, col2, col3, col4, empty = st.columns([2,2,2,2,1])
    with col1: st.markdown(kpi_box("Providers", total_providers), unsafe_allow_html=True)
    with col2: st.markdown(kpi_box("Receivers", total_receivers), unsafe_allow_html=True)
    with col3: st.markdown(kpi_box("Listings", total_listings), unsafe_allow_html=True)
    with col4: st.markdown(kpi_box("Claims", total_claims), unsafe_allow_html=True)

    st.markdown("### 🔎 CSV Queries")
    selected_query = st.selectbox("Choose a question:", list(provider_queries.keys()))
    if st.button("Generate Answer"):
        df = provider_queries[selected_query]()
        st.dataframe(df, use_container_width=True)
        st.info(descriptions[selected_query])

    st.markdown("### 🛠️ Run a Custom Pandas Query")
    st.text("You can use Python/pandas expressions here, e.g., food_listings.head()")
    custom_query = st.text_area("Enter your pandas code here (must return a DataFrame):")
    if st.button("Run Custom Query"):
        try:
            result = eval(custom_query)
            st.dataframe(result)
        except Exception as e:
            st.error(f"❌ Error in custom query: {e}")

# -------------------------
# Data Visualization Page
# -------------------------
elif menu == "Data Visualization":
    total_providers = get_count(providers)
    total_receivers = get_count(receivers)
    total_listings = get_count(food_listings)
    total_claims = get_count(claims)

    col1, col2, col3, col4, empty = st.columns([2,2,2,2,1])
    with col1: st.markdown(kpi_box("Providers", total_providers), unsafe_allow_html=True)
    with col2: st.markdown(kpi_box("Receivers", total_receivers), unsafe_allow_html=True)
    with col3: st.markdown(kpi_box("Listings", total_listings), unsafe_allow_html=True)
    with col4: st.markdown(kpi_box("Claims", total_claims), unsafe_allow_html=True)

    st.subheader("📊 Data Visualization")
    viz_options = [
        "Providers by City",
        "Claim Status Distribution",
        "Listings Over Time",
        "Claims by City",
        "Listings by Food Type",
        "Quantity vs Expiry Date",
        "Providers Contribution to Listings",
        "Claims Trend Over Time"
    ]
    selected_viz = st.selectbox("Select Visualization:", viz_options)

        # -------------------------
    # Dynamic Filters
    # -------------------------
    filter_option = None
    if selected_viz == "Providers by City":
        filter_option = st.selectbox("Filter Cities:", ["All", "Top 5", "Top 10"])
    elif selected_viz == "Claims by City":
        filter_option = st.selectbox("Filter Cities:", ["All", "Top 5", "Top 10"])
    elif selected_viz == "Listings by Food Type":
        types = ["All"] + food_listings["Food_Type"].dropna().unique().tolist()
        filter_option = st.selectbox("Filter by Food Type:", types)

    # -------------------------
    # Visualizations
    # -------------------------
    # Providers by City
    if selected_viz == "Providers by City":
        df = providers.groupby("City").size().reset_index(name="Provider_Count").sort_values("Provider_Count", ascending=False)
        if filter_option == "Top 5":
            df = df.head(5)
        elif filter_option == "Top 10":
            df = df.head(10)
        fig = px.bar(df, x="City", y="Provider_Count", title="Providers by City", color_discrete_sequence=["#1f3b73"])
        st.plotly_chart(fig)

    # Claim Status Distribution
    elif selected_viz == "Claim Status Distribution":
        df = claims.groupby("Status").size().reset_index(name="Count")
        fig = px.pie(df, names="Status", values="Count", title="Claim Status Distribution", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig)

    # Listings Over Time
    elif selected_viz == "Listings Over Time":
        df = food_listings.groupby(food_listings['Expiry_Date'].dt.date).size().reset_index(name="Listings").sort_values("Expiry_Date")
        fig = px.line(df, x="Expiry_Date", y="Listings", title="Listings Over Time", markers=True, line_shape="linear", color_discrete_sequence=["#FF7F50"])
        st.plotly_chart(fig)

    # Claims by City
    elif selected_viz == "Claims by City":
        merged = food_listings.merge(claims, on="Food_ID", how="left").merge(providers[['Provider_ID','City']], on="Provider_ID")
        df = merged.groupby("City")['Claim_ID'].count().reset_index(name="Total_Claims").sort_values("Total_Claims", ascending=False)
        if filter_option == "Top 5":
            df = df.head(5)
        elif filter_option == "Top 10":
            df = df.head(10)
        fig = px.bar(df, x="City", y="Total_Claims", title="Claims by City", color_discrete_sequence=["#8B0000"])
        st.plotly_chart(fig)

    # Listings by Food Type
    elif selected_viz == "Listings by Food Type":
        df = food_listings.groupby("Food_Type").size().reset_index(name="Total_Listings")
        if filter_option != "All":
            df = df[df["Food_Type"] == filter_option]
        fig = px.bar(df, x="Food_Type", y="Total_Listings", title="Listings by Food Type", color_discrete_sequence=["#006400"])
        st.plotly_chart(fig)

    # Quantity vs Expiry Date
    elif selected_viz == "Quantity vs Expiry Date":
        df = food_listings.dropna(subset=['Expiry_Date'])
        fig = px.scatter(df, x="Expiry_Date", y="Quantity", title="Quantity vs Expiry Date", color="Quantity", color_continuous_scale="Viridis")
        st.plotly_chart(fig)

    # Providers Contribution to Listings
    elif selected_viz == "Providers Contribution to Listings":
        df = food_listings.groupby("Provider_ID").size().reset_index(name="Listings").merge(providers[['Provider_ID','Name']], on="Provider_ID").sort_values("Listings", ascending=False).head(10)
        fig = px.bar(df, x="Listings", y="Name", orientation="h", title="Top Providers by Listings", color="Listings", color_continuous_scale="Cividis")
        st.plotly_chart(fig)

    # Claims Trend Over Time
    elif selected_viz == "Claims Trend Over Time":
        df = claims.dropna(subset=['Timestamp']).groupby(claims['Timestamp'].dt.date).size().reset_index(name="Total_Claims").sort_values("Timestamp")
        fig = px.area(df, x="Timestamp", y="Total_Claims", title="Claims Trend Over Time", color_discrete_sequence=["#FF69B4"])
        st.plotly_chart(fig)

# -------------------------
# Creator Info Page
# -------------------------
elif menu == "Creator Info":
    st.markdown("## 👨‍💻 Creator Information", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="padding:20px; background-color:#f1f1f1; border-radius:10px;">
            <h3 style="color:#333;">Developed By</h3>
            <p><b>Name:</b> Nithish Rexson L</p>
            <p><b>Role:</b> Aspiring Data Analyst</p>
            <p><b>About Me:</b> Passionate about data analysis, problem-solving, and building impactful digital solutions.</p>
            <p><b>Email:</b> nithishrex2020@gmail.com</p>
            <p><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/nithish-rexson/" target="_blank">linkedin.com/in/nithish-rexson</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

