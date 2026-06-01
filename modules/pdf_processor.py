"""
PDF Processing module
Extracts data from Illinois Conservation Police field reports
"""

import pdfplumber
import json
import re
from pathlib import Path
from typing import Dict, Any, List


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {e}")


def extract_tables_from_pdf(pdf_path: str) -> List[List[Dict]]:
    """Extract all tables from a PDF file"""
    try:
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        return tables
    except Exception as e:
        raise Exception(f"Error extracting tables from PDF: {e}")


def parse_field_report_text(text: str) -> Dict[str, Any]:
    """
    Parse Illinois Conservation Police field report text and extract key fields

    Args:
        text: Full extracted text from PDF

    Returns:
        Dictionary with parsed fields
    """
    data = {}

    # Extract field report number
    report_num_match = re.search(r'FIELD REPORT NUMBER\s*(\d{4}-\d+-\d+-\d+[A-Z]?)', text)
    if report_num_match:
        data['field_report_number'] = report_num_match.group(1)

    # Extract reporting officer
    officer_match = re.search(r'Reporting Officer and ID\s*([^\n]+)', text)
    if officer_match:
        data['reporting_officer'] = officer_match.group(1).strip()

    # Extract date reported
    date_match = re.search(r'DATE OCCURRED\s*(\d{1,2}/\d{1,2}/\d{4})', text)
    if date_match:
        data['date_occurred'] = date_match.group(1)

    # Extract time
    time_match = re.search(r'TIME\s*(\d{1,2}:\d{2}\s*(?:AM|PM))', text)
    if time_match:
        data['time_occurred'] = time_match.group(1)

    # Extract location
    location_match = re.search(r'LOCATION\s*([^\n]+?)\s+COUNTY', text)
    if location_match:
        data['location'] = location_match.group(1).strip()

    # Extract county
    county_match = re.search(r'COUNTY OF OCCURRENCE\s*([^\n]+)', text)
    if county_match:
        data['county'] = county_match.group(1).strip()

    # Extract complaint type
    complaint_match = re.search(r'COMPLAINT\s*([^\n]+?)(?:\n|LOCATION)', text)
    if complaint_match:
        data['complaint_type'] = complaint_match.group(1).strip()

    # Extract case status
    status_match = re.search(r'Case Status\s*(\w+)', text)
    if status_match:
        data['case_status'] = status_match.group(1).strip()

    # Extract subject name (Last, First)
    name_match = re.search(r'Last\s+([^\n]+?)\s+First\s+([^\n]+?)\s+M/I', text)
    if name_match:
        data['last_name'] = name_match.group(1).strip()
        data['first_name'] = name_match.group(2).strip()

    # Extract DOB
    dob_match = re.search(r'Date of Birth\s*(\d{1,2}/\d{1,2}/\d{4})', text)
    if dob_match:
        data['dob'] = dob_match.group(1)

    # Extract race/sex
    race_match = re.search(r'Race\s+([WBH])\s+Sex\s+([MF])', text)
    if race_match:
        data['race'] = race_match.group(1)
        data['sex'] = race_match.group(2)

    # Extract height/weight
    hw_match = re.search(r"Height\s+(['\"][\d\s\"]*)\s+Weight\s+(\d+)", text)
    if hw_match:
        data['height'] = hw_match.group(1).strip()
        data['weight'] = int(hw_match.group(2))

    # Extract address
    address_match = re.search(r'Street\s+([^\n]+?)\s+City\s+([^\n]+?)\s+State', text)
    if address_match:
        data['address'] = address_match.group(1).strip()
        data['city'] = address_match.group(2).strip()

    # Extract state/zip
    state_zip_match = re.search(r'State\s+([A-Z]{2})\s+Zip\s+(\d{5})', text)
    if state_zip_match:
        data['state'] = state_zip_match.group(1)
        data['zip'] = state_zip_match.group(2)

    # Extract phone
    phone_match = re.search(r'Telephone\s+([^\n]+)', text)
    if phone_match:
        data['phone'] = phone_match.group(1).strip()

    # Extract charges/citations
    charges = []
    charge_pattern = r'(\d+[A-Z]*)\s+(\d{3}/\d{1,2}/\d{1,2}[.\d]*)\s+([^\n]+)'
    for match in re.finditer(charge_pattern, text):
        charges.append({
            'citation_code': match.group(1),
            'chapter_act': match.group(2),
            'description': match.group(3).strip()
        })
    if charges:
        data['charges'] = charges

    # Extract narrative (everything between NARRATIVE and SYNOPSIS or next section)
    narrative_match = re.search(r'NARRATIVE\s*(.+?)(?=SYNOPSIS|PHOTOGRAPHIC|EVIDENCE|$)', text, re.DOTALL)
    if narrative_match:
        data['narrative'] = narrative_match.group(1).strip()

    # Extract synopsis
    synopsis_match = re.search(r'SYNOPSIS\s*(.+?)(?=NARRATIVE|PHOTOGRAPHIC|EVIDENCE|$)', text, re.DOTALL)
    if synopsis_match:
        data['synopsis'] = synopsis_match.group(1).strip()

    return data


def parse_pdf_report(pdf_path: str, report_name: str = None) -> Dict[str, Any]:
    """
    Parse a complete Illinois Conservation Police field report PDF

    Args:
        pdf_path: Path to the PDF file
        report_name: Optional report name (defaults to filename)

    Returns:
        Dictionary with extracted report data
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if report_name is None:
        report_name = Path(pdf_path).stem

    try:
        # Extract full text
        full_text = extract_text_from_pdf(pdf_path)

        # Parse structured fields from text
        parsed_fields = parse_field_report_text(full_text)

        # Get tables (for evidence, vehicle info, etc.)
        tables = extract_tables_from_pdf(pdf_path)

        # Get page count
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)

        # Combine extracted data
        extracted_data = {
            **parsed_fields,
            "full_text": full_text,
            "tables": tables,
            "num_pages": num_pages
        }

        # Structure the report
        report = {
            "report_name": report_name,
            "source_file": Path(pdf_path).name,
            "extracted_data": extracted_data,
            "extraction_status": "success"
        }

        return report
    except Exception as e:
        return {
            "report_name": report_name,
            "source_file": Path(pdf_path).name,
            "extracted_data": {"full_text": "Error during extraction"},
            "extraction_status": "error",
            "error_message": str(e)
        }


def batch_process_pdfs(pdf_directory: str, output_json: str = None) -> List[Dict[str, Any]]:
    """Process multiple PDFs in a directory"""
    pdf_dir = Path(pdf_directory)

    if not pdf_dir.exists():
        raise FileNotFoundError(f"Directory not found: {pdf_directory}")

    results = []
    pdf_files = sorted(list(pdf_dir.glob("*.pdf")))

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        report = parse_pdf_report(str(pdf_file))
        results.append(report)

    if output_json:
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {output_json}")

    return results


def validate_pdf(pdf_path: str) -> Dict[str, Any]:
    """Validate that a PDF can be read and contains data"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            has_text = False
            has_tables = False

            for page in pdf.pages:
                if page.extract_text():
                    has_text = True
                if page.extract_tables():
                    has_tables = True

            return {
                "valid": True,
                "num_pages": num_pages,
                "has_text": has_text,
                "has_tables": has_tables,
                "error": None
            }
    except Exception as e:
        return {
            "valid": False,
            "num_pages": 0,
            "has_text": False,
            "has_tables": False,
            "error": str(e)
        }
