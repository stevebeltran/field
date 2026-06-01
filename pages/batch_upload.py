"""
Batch Upload page - Upload PDF field reports to the database
"""

import streamlit as st
from modules.pdf_processor import parse_pdf_report
from modules.database import create_report
import tempfile
from pathlib import Path
import time
import gc


def run():
    """Run the batch upload page"""

    # Upload mode selection
    col1, col2 = st.columns(2)
    with col1:
        upload_mode = st.radio(
            "Upload Mode",
            ["Single File", "Batch Upload"],
            help="Choose how to upload your PDFs"
        )

    with col2:
        st.info("💡 Tip: Use batch upload for multiple files at once")

    st.divider()

    if upload_mode == "Single File":
        render_single_upload()
    else:
        render_batch_upload()


def render_single_upload():
    """Render single file upload interface"""

    st.subheader("Upload Single PDF Report")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Select a field report PDF"
    )

    if uploaded_file is not None:
        st.write(f"**File**: {uploaded_file.name}")
        st.write(f"**Size**: {uploaded_file.size / 1024:.2f} KB")

        # Optional custom report name
        report_name = st.text_input(
            "Report Name (optional)",
            value=uploaded_file.name.replace(".pdf", ""),
            help="Custom name for this report. If empty, filename will be used."
        )

        notes = st.text_area(
            "Notes (optional)",
            help="Add any notes about this report"
        )

        if st.button("📤 Upload and Process", type="primary"):
            with st.spinner("Processing PDF..."):
                tmp_path = None
                try:
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name

                    # Parse PDF
                    report_data = parse_pdf_report(tmp_path, report_name or uploaded_file.name)

                    if report_data["extraction_status"] == "success":
                        # Save to database
                        db_report = create_report(
                            report_name=report_name or uploaded_file.name.replace(".pdf", ""),
                            report_type="pdf_import",
                            field_data=report_data["extracted_data"],
                            source_file=uploaded_file.name,
                            notes=notes
                        )

                        st.success(f"✅ Report uploaded successfully! (ID: {db_report.id})")
                        st.write(f"**Report Name**: {db_report.report_name}")
                        st.write(f"**Created**: {db_report.created_date}")

                    else:
                        st.error(f"❌ Error extracting PDF: {report_data.get('error_message', 'Unknown error')}")

                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

                finally:
                    # Cleanup temp file
                    if tmp_path:
                        try:
                            gc.collect()
                            time.sleep(0.5)
                            Path(tmp_path).unlink(missing_ok=True)
                        except Exception as cleanup_error:
                            st.warning(f"Could not delete temp file: {cleanup_error}")


def render_batch_upload():
    """Render batch upload interface"""

    st.subheader("Batch Upload Multiple PDF Reports")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="Select multiple field report PDFs"
    )

    if uploaded_files:
        st.write(f"**Files selected**: {len(uploaded_files)}")

        # Show file list
        with st.expander("View selected files"):
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.size / 1024:.2f} KB)")

        # Batch notes
        batch_notes = st.text_area(
            "Batch Notes (optional)",
            help="Notes to add to all uploaded reports"
        )

        if st.button("📤 Process All Files", type="primary"):
            progress_bar = st.progress(0)
            status_container = st.container()

            successful = 0
            failed = 0
            errors = []

            for idx, uploaded_file in enumerate(uploaded_files):
                with st.spinner(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}"):
                    tmp_path = None
                    try:
                        # Save to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.getbuffer())
                            tmp_path = tmp_file.name

                        # Parse PDF
                        report_data = parse_pdf_report(tmp_path, uploaded_file.name)

                        if report_data["extraction_status"] == "success":
                            # Save to database
                            db_report = create_report(
                                report_name=uploaded_file.name.replace(".pdf", ""),
                                report_type="pdf_import",
                                field_data=report_data["extracted_data"],
                                source_file=uploaded_file.name,
                                notes=batch_notes
                            )
                            successful += 1
                        else:
                            failed += 1
                            errors.append(f"{uploaded_file.name}: {report_data.get('error_message', 'Unknown error')}")

                    except Exception as e:
                        failed += 1
                        errors.append(f"{uploaded_file.name}: {str(e)}")

                    finally:
                        # Cleanup temp file
                        if tmp_path:
                            try:
                                gc.collect()
                                time.sleep(0.1)
                                Path(tmp_path).unlink(missing_ok=True)
                            except Exception:
                                pass  # Silently ignore cleanup errors in batch

                progress_bar.progress((idx + 1) / len(uploaded_files))

            # Show results
            st.divider()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Successful", successful)
            with col2:
                st.metric("❌ Failed", failed)
            with col3:
                st.metric("Total", len(uploaded_files))

            if successful > 0:
                st.success(f"Successfully uploaded {successful} report(s)")

            if errors:
                with st.expander("View Errors"):
                    for error in errors:
                        st.error(error)
