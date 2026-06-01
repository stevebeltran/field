"""
Create Report page - Create new field reports
"""

import streamlit as st
from modules.database import create_report
from modules.forms import DynamicFormBuilder, get_default_report_schema
from datetime import datetime


def run():
    """Run the create report page"""

    st.subheader("Create a New Field Report")

    # Get form schema
    schema = get_default_report_schema()

    # Initialize form builder
    form_builder = DynamicFormBuilder(schema)

    # Use Streamlit form
    with st.form("field_report_form", clear_on_submit=True):
        # Basic Information Section
        st.subheader("📋 Basic Information")
        basic_info = form_builder.render_form_section("Basic Info", schema["basic_info"])

        st.divider()

        # Observations Section
        st.subheader("👁️ Observations")
        observations = form_builder.render_form_section("Observations", schema["observations"])

        st.divider()

        # Additional Details
        st.subheader("📝 Additional Details")

        assigned_to = st.text_input(
            "Assigned To (optional)",
            help="Who is responsible for this report?"
        )

        additional_notes = st.text_area(
            "Additional Notes (optional)",
            height=150,
            help="Any extra information about this report"
        )

        st.divider()

        # Submit button
        submitted = st.form_submit_button("💾 Save Report", type="primary", use_container_width=True)

        if submitted:
            # Combine all form data
            report_data = {
                **basic_info,
                **observations,
                "assigned_to": assigned_to,
                "additional_notes": additional_notes,
                "created_by": "user",  # Will be replaced with SSO username later
                "created_at": datetime.now().isoformat()
            }

            try:
                # Get report title from form
                report_title = basic_info.get("report_title", "Untitled Report")

                # Save to database
                db_report = create_report(
                    report_name=report_title,
                    report_type="new_report",
                    field_data=report_data,
                    created_by=assigned_to or "user",
                    notes=additional_notes
                )

                st.success(f"✅ Report created successfully!")
                st.info(f"**Report ID**: {db_report.id}")
                st.write(f"**Title**: {report_title}")
                st.write(f"**Created**: {db_report.created_date}")

            except Exception as e:
                st.error(f"❌ Error saving report: {e}")

    # Show recent reports
    st.divider()
    st.subheader("📚 Recently Created Reports")

    try:
        from modules.database import search_reports
        recent_reports = search_reports(report_type="new_report", limit=5)

        if recent_reports:
            for report in recent_reports:
                with st.expander(f"📄 {report.report_name} ({report.created_date.strftime('%Y-%m-%d %H:%M')})"):
                    st.write(f"**ID**: {report.id}")
                    st.write(f"**Created**: {report.created_date}")

                    if report.notes:
                        st.write(f"**Notes**: {report.notes}")

                    if st.button("View Full Report", key=f"view_{report.id}"):
                        st.json(report.field_data)
        else:
            st.info("No reports created yet. Create your first one above!")

    except Exception as e:
        st.warning(f"Could not load recent reports: {e}")
