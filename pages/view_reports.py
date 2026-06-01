"""
View Reports page - Search and display field reports
"""

import streamlit as st
from modules.database import search_reports, get_report, delete_report
import pandas as pd
from datetime import datetime


def run():
    """Run the view reports page"""

    st.subheader("Search & View Field Reports")

    # Search filters
    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input(
            "🔍 Search by name or source",
            placeholder="Enter report name or filename..."
        )

    with col2:
        report_type = st.selectbox(
            "📂 Filter by type",
            ["All", "PDF Imports", "New Reports"],
            help="Show all types or filter by source"
        )

    with col3:
        limit = st.slider(
            "📊 Results per page",
            min_value=5,
            max_value=100,
            value=20,
            step=5
        )

    st.divider()

    # Convert filter
    type_filter = None
    if report_type == "PDF Imports":
        type_filter = "pdf_import"
    elif report_type == "New Reports":
        type_filter = "new_report"

    # Search
    try:
        reports = search_reports(search_term=search_term, report_type=type_filter, limit=limit)

        if reports:
            st.success(f"Found {len(reports)} report(s)")

            # Create table view
            table_data = []
            for report in reports:
                table_data.append({
                    "ID": report.id,
                    "Name": report.report_name,
                    "Type": "PDF" if report.report_type == "pdf_import" else "New",
                    "Created": report.created_date.strftime("%Y-%m-%d %H:%M"),
                    "Source": report.source_file or "-"
                })

            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()

            # Individual report display
            st.subheader("📖 Report Details")

            selected_id = st.selectbox(
                "Select a report to view details",
                options=[r["ID"] for r in table_data],
                format_func=lambda x: f"ID {x} - {next(r['Name'] for r in table_data if r['ID'] == x)}"
            )

            if selected_id:
                report = get_report(selected_id)

                if report:
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Report ID", report.id)
                    with col2:
                        st.metric("Type", "PDF Import" if report.report_type == "pdf_import" else "New Report")
                    with col3:
                        st.metric("Created", report.created_date.strftime("%Y-%m-%d"))

                    st.divider()

                    # Report metadata
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Report Name**: {report.report_name}")
                        if report.source_file:
                            st.write(f"**Source File**: {report.source_file}")

                    with col2:
                        st.write(f"**Created**: {report.created_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Updated**: {report.updated_date.strftime('%Y-%m-%d %H:%M:%S')}")

                    if report.notes:
                        st.info(f"**Notes**: {report.notes}")

                    st.divider()

                    # Data display
                    st.subheader("📋 Report Data")

                    # Show as JSON
                    view_format = st.radio(
                        "View format",
                        ["Formatted", "Raw JSON"],
                        horizontal=True
                    )

                    if view_format == "Formatted":
                        display_formatted_data(report.field_data)
                    else:
                        st.json(report.field_data)

                    st.divider()

                    # Actions
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("📥 Export as JSON", key=f"export_{report.id}"):
                            st.download_button(
                                label="Download JSON",
                                data=str(report.field_data),
                                file_name=f"report_{report.id}.json",
                                mime="application/json"
                            )

                    with col2:
                        if st.button("🗑️ Delete Report", key=f"delete_{report.id}"):
                            if st.confirmation_checkbox("Are you sure you want to delete this report?"):
                                if delete_report(report.id):
                                    st.success("Report deleted successfully")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete report")

        else:
            st.info("No reports found. Try adjusting your search filters or create a new report.")

    except Exception as e:
        st.error(f"Error searching reports: {e}")


def display_formatted_data(data, indent=0):
    """Display data in a formatted way"""

    for key, value in data.items():
        if isinstance(value, dict):
            st.write(f"**{key}**")
            display_formatted_data(value, indent + 1)
        elif isinstance(value, list):
            st.write(f"**{key}**")
            for idx, item in enumerate(value):
                if isinstance(item, dict):
                    st.write(f"  Item {idx + 1}:")
                    display_formatted_data(item, indent + 2)
                else:
                    st.write(f"  • {item}")
        else:
            st.write(f"**{key}**: {value}")
