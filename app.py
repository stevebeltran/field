"""
Field Reports System - Main Streamlit Application
"""

import streamlit as st
from modules.database import test_connection, init_db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# 🔐 AUTHENTICATION
# ============================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Show login page
    st.set_page_config(
        page_title="Field Reports - Login",
        page_icon="🔐",
        layout="centered"
    )

    st.markdown("""
    <div style='text-align: center; padding: 50px 0;'>
        <h1>🔐 Field Reports System</h1>
        <p style='color: gray;'>Illinois Conservation Police</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Enter password:", type="password", key="login_password")

        if st.button("🔓 Login", use_container_width=True, type="primary"):
            # Get password from secrets, default to 'demo' if not set
            correct_password = st.secrets.get("APP_PASSWORD", "demo")

            if password == correct_password:
                st.session_state.authenticated = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid password. Please try again.")

    st.info("💡 Default password: `demo` (Change in Streamlit Secrets)")
    st.stop()

# ============================================
# END AUTHENTICATION
# ============================================

# Page configuration
st.set_page_config(
    page_title="Field Reports System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on first run
if "db_initialized" not in st.session_state:
    try:
        if test_connection():
            init_db()
            st.session_state.db_initialized = True
            st.success("✅ Database connection established and initialized!")
        else:
            st.error("❌ Unable to connect to database. Please check your .env configuration.")
            st.session_state.db_initialized = False
    except Exception as e:
        st.error(f"❌ Database initialization error: {e}")
        st.session_state.db_initialized = False

# Sidebar navigation
st.sidebar.title("📋 Field Reports System")

# Logout button
st.sidebar.divider()
col1, col2 = st.sidebar.columns([3, 1])
with col1:
    st.sidebar.write(f"**Logged in** ✅")
with col2:
    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        st.session_state.authenticated = False
        st.rerun()

st.sidebar.divider()

if st.session_state.get("db_initialized", False):
    st.sidebar.info("✅ Database Connected")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📤 Batch Upload",
            "✏️ Create Report",
            "📖 View Reports",
            "⚙️ Settings"
        ]
    )

    # Route pages
    if page == "🏠 Home":
        st.title("📋 Field Reports System")
        st.markdown("""
        Welcome to the Field Reports System!

        This application allows you to:
        - **📤 Upload old PDF field reports** in batch
        - **✏️ Create new field reports** with dynamic forms
        - **📖 Search and view all reports** with full data retrieval

        ### Getting Started

        1. **Batch Upload PDFs**: Use the "Batch Upload" page to import your existing PDF field reports
        2. **Create New Reports**: Use the "Create Report" page to generate new field reports
        3. **View & Search**: Navigate to "View Reports" to search across all your data

        All data is stored securely in your MySQL database on omnis.com.

        ### Features

        - ✅ Consistent PDF template parsing
        - ✅ Dynamic form fields that expand with data
        - ✅ Full-text search across all fields
        - ✅ Historical data preservation from PDFs
        - ✅ User-friendly interface

        ### Next Steps

        👉 Start by uploading your PDF reports or creating a new one!
        """)

        # Show some stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        try:
            from modules.database import search_reports
            all_reports = search_reports()
            pdf_reports = search_reports(report_type="pdf_import")
            new_reports = search_reports(report_type="new_report")

            with col1:
                st.metric("Total Reports", len(all_reports))
            with col2:
                st.metric("Imported PDFs", len(pdf_reports))
            with col3:
                st.metric("New Reports", len(new_reports))
        except Exception as e:
            st.warning(f"Could not load report statistics: {e}")

    elif page == "📤 Batch Upload":
        st.title("📤 Batch Upload PDF Reports")
        st.markdown("Upload your PDF field reports in batch to the database.")

        from pages import batch_upload
        batch_upload.run()

    elif page == "✏️ Create Report":
        st.title("✏️ Create New Field Report")
        st.markdown("Create a new field report with dynamic, expandable fields.")

        from pages import create_report
        create_report.run()

    elif page == "📖 View Reports":
        st.title("📖 View & Search Reports")
        st.markdown("Search and view all field reports (PDF and new).")

        from pages import view_reports
        view_reports.run()

    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")

        st.subheader("Database Configuration")
        st.info(f"**Database Host**: {os.getenv('DB_HOST')}")
        st.info(f"**Database Name**: {os.getenv('DB_NAME')}")

        if st.button("🔄 Test Database Connection"):
            if test_connection():
                st.success("✅ Database connection successful!")
            else:
                st.error("❌ Database connection failed!")

        st.divider()

        st.subheader("Application Info")
        st.markdown("""
        **Field Reports System v1.0**

        Built with:
        - Streamlit
        - Python
        - MySQL/MariaDB
        - PDFPlumber

        For support: steven.beltran@brincdrones.com
        """)

else:
    st.error("❌ Database Not Connected")
    st.markdown("""
    The application cannot connect to the database.

    **Please check:**
    1. Create a `.env` file in the field directory
    2. Copy settings from `.env.example`
    3. Fill in your MySQL database credentials from omnis.com
    4. Refresh the page

    **Example .env file:**
    ```
    DB_HOST=your_host.com
    DB_PORT=3306
    DB_USER=your_username
    DB_PASSWORD=your_password
    DB_NAME=your_database
    ```
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Field Reports System | Powered by Streamlit & Python
    </div>
    """,
    unsafe_allow_html=True
)
