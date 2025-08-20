# -------------------------
# Imports
# -------------------------
import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px 
# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Food Waste Management System", layout="wide")

# -------------------------
# Database connection
# -------------------------
def create_connection():
    connection = mysql.connector.connect(
        host="localhost",        
        user="root",             
        password="Nithish@12345", 
        database="food_management"  
    )
    return connection

# -------------------------
# Get counts
# -------------------------
def get_count(table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# -------------------------
# Define Queries (Global)
# -------------------------
provider_queries = {
    "1. List all providers": """
        SELECT Provider_ID, Name, Type, City, Contact
        FROM providers
        LIMIT 20;
    """,
    "2. Count of providers by city": """
        SELECT City, COUNT(*) AS Provider_Count
        FROM providers
        GROUP BY City
        ORDER BY Provider_Count DESC;
    """,
    "3. Providers with most listings": """
        SELECT p.Name, COUNT(f.Food_ID) AS Total_Listings
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Name
        ORDER BY Total_Listings DESC
        LIMIT 10;
    """,

    "4. Top 5 providers with maximum claims": """
        SELECT p.Name, COUNT(c.Claim_ID) AS Total_Claims
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY p.Name
        ORDER BY Total_Claims DESC
        LIMIT 5;
    """,
    "5. Providers with expired food listings": """
        SELECT DISTINCT p.Name, COUNT(f.Food_ID) AS Expired_Listings
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        WHERE f.Expiry_Date < CURDATE()
        GROUP BY p.Name
        ORDER BY Expired_Listings DESC;
    """,
    "6. Average food quantity provided per provider": """
        SELECT p.Name, AVG(f.Quantity) AS Avg_Quantity
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Name
        ORDER BY Avg_Quantity DESC;
    """,
    "7. Provider with maximum unique receivers": """
        SELECT p.Name, COUNT(DISTINCT c.Receiver_ID) AS Unique_Receivers
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY p.Name
        ORDER BY Unique_Receivers DESC
        LIMIT 1;
    """,
    "8. Percentage contribution of each provider to total listings": """
        SELECT p.Name,
               COUNT(f.Food_ID) * 100.0 / (SELECT COUNT(*) FROM food_listings) AS Contribution_Percentage
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Name
        ORDER BY Contribution_Percentage DESC;
    """,
    "9. Providers with zero claims": """
        SELECT p.Name
        FROM providers p
        LEFT JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        LEFT JOIN claims c ON f.Food_ID = c.Food_ID
        WHERE c.Claim_ID IS NULL;
    """,
    "10. City-wise claim distribution for providers": """
        SELECT p.City, COUNT(c.Claim_ID) AS Total_Claims
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY p.City
        ORDER BY Total_Claims DESC;
    """,
    "11. Top providers by completed claims": """
        SELECT p.Name, COUNT(c.Claim_ID) AS Completed_Claims
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        JOIN claims c ON f.Food_ID = c.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Name
        ORDER BY Completed_Claims DESC
        LIMIT 5;
    """,
    "12. Claim status breakdown per provider": """
        SELECT p.Name, c.Status, COUNT(*) AS Count
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        JOIN claims c ON c.Food_ID = f.Food_ID
        GROUP BY p.Name, c.Status
        ORDER BY p.Name, Count DESC;
    """
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
            <li><b>SQL Analysis:</b> Powerful insights using SQL queries.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# Dashboard Page
# -------------------------
elif menu == "Dashboard":
    try:
        total_providers = get_count("providers")
        total_receivers = get_count("receivers")
        total_listings = get_count("food_listings")
        total_claims = get_count("claims")

        col1, col2, col3, col4, empty = st.columns([2,2,2,2,1])
        with col1: st.markdown(kpi_box("Providers", total_providers), unsafe_allow_html=True)
        with col2: st.markdown(kpi_box("Receivers", total_receivers), unsafe_allow_html=True)
        with col3: st.markdown(kpi_box("Listings", total_listings), unsafe_allow_html=True)
        with col4: st.markdown(kpi_box("Claims", total_claims), unsafe_allow_html=True)

        st.markdown("### 📂 Explore Tables")
        tables = ["providers", "receivers", "food_listings", "claims"]
        selected_table = st.selectbox("Select a table to view:", tables)

        if st.button("Generate Table"):
            conn = create_connection()
            df = pd.read_sql(f"SELECT * FROM {selected_table} LIMIT 20;", conn)
            conn.close()
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error fetching KPI data: {e}")

# -------------------------
# Queries Page
# -------------------------
elif menu == "Queries":
    try:
        total_providers = get_count("providers")
        total_receivers = get_count("receivers")
        total_listings = get_count("food_listings")
        total_claims = get_count("claims")

        col1, col2, col3, col4, empty = st.columns([2,2,2,2,1])
        with col1: st.markdown(kpi_box("Providers", total_providers), unsafe_allow_html=True)
        with col2: st.markdown(kpi_box("Receivers", total_receivers), unsafe_allow_html=True)
        with col3: st.markdown(kpi_box("Listings", total_listings), unsafe_allow_html=True)
        with col4: st.markdown(kpi_box("Claims", total_claims), unsafe_allow_html=True)

        st.markdown("### 🔎 SQL Queries")
        selected_query = st.selectbox("Choose a question:", list(provider_queries.keys()))

        if st.button("Generate Answer"):
            try:
                conn = create_connection()
                df = pd.read_sql(provider_queries[selected_query], conn)
                conn.close()
                st.dataframe(df, use_container_width=True)
                st.info(descriptions[selected_query])
            except Exception as e:
                st.error(f"❌ Error running query: {e}")

        st.markdown("### 🛠️ Run a Custom SQL Query")
        custom_sql = st.text_area("Enter your SQL query here:")
        if st.button("Run Custom Query"):
            try:
                conn = create_connection()
                df = pd.read_sql(custom_sql, conn)
                conn.close()
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error in custom query: {e}")

    except Exception as e:
        st.error(f"❌ Error in Queries page: {e}")

# -------------------------
# Data Visualization Page
# -------------------------
elif menu == "Data Visualization":
    try:
        # KPIs
        total_providers = get_count("providers")
        total_receivers = get_count("receivers")
        total_listings = get_count("food_listings")
        total_claims = get_count("claims")

        col1, col2, col3, col4, empty = st.columns([2,2,2,2,1])
        with col1: st.markdown(kpi_box("Providers", total_providers), unsafe_allow_html=True)
        with col2: st.markdown(kpi_box("Receivers", total_receivers), unsafe_allow_html=True)
        with col3: st.markdown(kpi_box("Listings", total_listings), unsafe_allow_html=True)
        with col4: st.markdown(kpi_box("Claims", total_claims), unsafe_allow_html=True)

        st.subheader("📊 Data Visualization")

        # Select Visualization
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

        # Dynamic Filters
        filter_option = None
        if selected_viz == "Providers by City":
            filter_option = st.selectbox("Filter Cities:", ["All", "Top 5", "Top 10"])
        elif selected_viz == "Claims by City":
            filter_option = st.selectbox("Filter Cities:", ["All", "Top 5", "Top 10"])
        elif selected_viz == "Listings by Food Type":
            filter_option = st.selectbox("Filter by Food Type:", ["All", "Vegetarian", "Non-Vegetarian", "Vegan"])

        # Fetch Data + Visualization
        conn = create_connection()

        if selected_viz == "Providers by City":
            query = "SELECT City, COUNT(*) AS Provider_Count FROM providers GROUP BY City ORDER BY Provider_Count DESC"
            df = pd.read_sql(query, conn)
            if filter_option == "Top 5":
                df = df.head(5)
            elif filter_option == "Top 10":
                df = df.head(10)
            # Dark Blue
            fig = px.bar(df, x="City", y="Provider_Count",
                         title="Providers by City",
                         color_discrete_sequence=["#1f3b73"])
            st.plotly_chart(fig)

        elif selected_viz == "Claim Status Distribution":
            query = "SELECT Status, COUNT(*) AS Count FROM claims GROUP BY Status"
            df = pd.read_sql(query, conn)
            fig = px.pie(df, names="Status", values="Count", title="Claim Status Distribution",
                         color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig)

        elif selected_viz == "Listings Over Time":
            query = """
                SELECT DATE(Expiry_Date) AS Date, COUNT(*) AS Listings
                FROM food_listings
                WHERE Expiry_Date IS NOT NULL
                GROUP BY DATE(Expiry_Date)
                ORDER BY Date
            """
            df = pd.read_sql(query, conn)
            fig = px.line(df, x="Date", y="Listings", title="Listings Over Time",
                          markers=True, line_shape="linear", color_discrete_sequence=["#FF7F50"])
            st.plotly_chart(fig)

        elif selected_viz == "Claims by City":
            query = """
                SELECT f.Location AS City, COUNT(*) AS Total_Claims
                FROM food_listings f
                JOIN providers p ON f.Provider_ID = p.Provider_ID
                JOIN claims c ON f.Food_ID = c.Food_ID
                GROUP BY f.Location
                ORDER BY Total_Claims DESC
            """
            df = pd.read_sql(query, conn)
            if filter_option == "Top 5":
                df = df.head(5)
            elif filter_option == "Top 10":
                df = df.head(10)
            # Dark Red
            fig = px.bar(df, x="City", y="Total_Claims",
                         title="Claims by City",
                         color_discrete_sequence=["#8B0000"])
            st.plotly_chart(fig)

        elif selected_viz == "Listings by Food Type":
            query = "SELECT Food_Type, COUNT(*) AS Total_Listings FROM food_listings GROUP BY Food_Type"
            df = pd.read_sql(query, conn)
            if filter_option != "All":
                df = df[df["Food_Type"] == filter_option]
            # Dark Green
            fig = px.bar(df, x="Food_Type", y="Total_Listings",
                         title="Listings by Food Type",
                         color_discrete_sequence=["#006400"])
            st.plotly_chart(fig)

        elif selected_viz == "Quantity vs Expiry Date":
            query = "SELECT Quantity, Expiry_Date FROM food_listings WHERE Expiry_Date IS NOT NULL"
            df = pd.read_sql(query, conn)
            fig = px.scatter(df, x="Expiry_Date", y="Quantity", title="Quantity vs Expiry Date",
                             color="Quantity", color_continuous_scale="Viridis")
            st.plotly_chart(fig)

        elif selected_viz == "Providers Contribution to Listings":
            query = """
                SELECT p.Name, COUNT(f.Food_ID) AS Listings
                FROM providers p
                JOIN food_listings f ON p.Provider_ID = f.Provider_ID
                GROUP BY p.Name
                ORDER BY Listings DESC
                LIMIT 10
            """
            df = pd.read_sql(query, conn)
            fig = px.bar(df, x="Listings", y="Name", orientation="h",
                         title="Top Providers by Listings",
                         color="Listings", color_continuous_scale="Cividis")
            st.plotly_chart(fig)

        elif selected_viz == "Claims Trend Over Time":
            query = """
                SELECT DATE(Timestamp) AS Date, COUNT(*) AS Total_Claims
                FROM claims
                WHERE Timestamp IS NOT NULL
                GROUP BY DATE(Timestamp)
                ORDER BY Date
            """
            df = pd.read_sql(query, conn)
            fig = px.area(df, x="Date", y="Total_Claims", title="Claims Trend Over Time",
                          color_discrete_sequence=["#FF69B4"])
            st.plotly_chart(fig)

        conn.close()

    except Exception as e:
        st.error(f"❌ Error in Data Visualization page: {e}")

# -------------------------
# Creator Info Page
# -------------------------
if menu == "Creator Info":
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









