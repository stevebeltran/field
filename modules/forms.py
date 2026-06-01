"""
Dynamic form generation for Field Reports
"""

import streamlit as st
from typing import Dict, Any, List, Tuple


class DynamicFormBuilder:
    """Build dynamic forms in Streamlit based on field definitions"""

    def __init__(self, form_schema: Dict[str, Any] = None):
        """
        Initialize form builder

        Args:
            form_schema: Dictionary defining form structure
        """
        self.form_schema = form_schema or {}

    def render_text_field(self, key: str, label: str, required: bool = False, value: str = "") -> str:
        """Render a text input field"""
        return st.text_input(
            label=label,
            value=value,
            key=key,
            help="Enter text information"
        )

    def render_number_field(self, key: str, label: str, required: bool = False, value: float = 0) -> float:
        """Render a number input field"""
        return st.number_input(
            label=label,
            value=value,
            key=key,
            help="Enter numeric value"
        )

    def render_date_field(self, key: str, label: str, required: bool = False) -> Any:
        """Render a date input field"""
        return st.date_input(
            label=label,
            key=key,
            help="Select a date"
        )

    def render_textarea_field(self, key: str, label: str, required: bool = False, value: str = "") -> str:
        """Render a textarea field"""
        return st.text_area(
            label=label,
            value=value,
            key=key,
            height=100,
            help="Enter multi-line text"
        )

    def render_select_field(self, key: str, label: str, options: List[str], required: bool = False, value: str = None) -> str:
        """Render a select dropdown field"""
        if value is None and options:
            value = options[0]

        return st.selectbox(
            label=label,
            options=options,
            index=options.index(value) if value in options else 0,
            key=key,
            help="Select from available options"
        )

    def render_multiselect_field(self, key: str, label: str, options: List[str], value: List[str] = None) -> List[str]:
        """Render a multi-select field"""
        if value is None:
            value = []

        return st.multiselect(
            label=label,
            options=options,
            default=value,
            key=key,
            help="Select one or more options"
        )

    def render_checkbox_field(self, key: str, label: str, value: bool = False) -> bool:
        """Render a checkbox field"""
        return st.checkbox(
            label=label,
            value=value,
            key=key,
            help="Check to enable"
        )

    def render_field(self, field_key: str, field_def: Dict[str, Any]) -> Tuple[str, Any]:
        """
        Render a single field based on its definition

        Args:
            field_key: Unique key for the field
            field_def: Field definition dictionary

        Returns:
            Tuple of (field_key, field_value)
        """
        field_type = field_def.get("type", "text")
        label = field_def.get("label", field_key)
        required = field_def.get("required", False)
        value = field_def.get("value", None)

        if field_type == "text":
            result = self.render_text_field(field_key, label, required, value or "")
        elif field_type == "number":
            result = self.render_number_field(field_key, label, required, value or 0)
        elif field_type == "date":
            result = self.render_date_field(field_key, label, required)
        elif field_type == "textarea":
            result = self.render_textarea_field(field_key, label, required, value or "")
        elif field_type == "select":
            options = field_def.get("options", [])
            result = self.render_select_field(field_key, label, options, required, value)
        elif field_type == "multiselect":
            options = field_def.get("options", [])
            result = self.render_multiselect_field(field_key, label, options, value or [])
        elif field_type == "checkbox":
            result = self.render_checkbox_field(field_key, label, value or False)
        else:
            st.warning(f"Unknown field type: {field_type}")
            result = None

        return field_key, result

    def render_form_section(self, section_name: str, fields: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Render a section of the form with multiple fields

        Args:
            section_name: Name of the form section
            fields: Dictionary of field definitions

        Returns:
            Dictionary of field values
        """
        st.subheader(section_name)

        section_data = {}
        for field_key, field_def in fields.items():
            key, value = self.render_field(field_key, field_def)
            section_data[key] = value

        return section_data

    def render_expandable_section(self, section_name: str, fields: Dict[str, Dict[str, Any]], max_items: int = None) -> List[Dict[str, Any]]:
        """
        Render an expandable section where users can add multiple entries

        Args:
            section_name: Name of the expandable section
            fields: Dictionary of field definitions for each item
            max_items: Maximum number of items allowed

        Returns:
            List of dictionaries, each containing field values
        """
        st.subheader(section_name)

        if f"{section_name}_count" not in st.session_state:
            st.session_state[f"{section_name}_count"] = 1

        items = []
        num_items = st.session_state[f"{section_name}_count"]

        for item_num in range(1, num_items + 1):
            with st.expander(f"{section_name} #{item_num}"):
                item_data = {}
                for field_key, field_def in fields.items():
                    unique_key = f"{section_name}_{item_num}_{field_key}"
                    key, value = self.render_field(unique_key, field_def)
                    item_data[field_key] = value
                items.append(item_data)

        # Add/Remove buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Add {section_name}", key=f"add_{section_name}"):
                if max_items is None or num_items < max_items:
                    st.session_state[f"{section_name}_count"] += 1
                    st.rerun()

        with col2:
            if num_items > 1:
                if st.button(f"Remove {section_name}", key=f"remove_{section_name}"):
                    st.session_state[f"{section_name}_count"] -= 1
                    st.rerun()

        return items


def get_default_report_schema() -> Dict[str, Any]:
    """Get Illinois Conservation Police field report schema"""
    return {
        "report_header": {
            "field_report_number": {
                "type": "text",
                "label": "Field Report Number",
                "required": True,
                "value": ""
            },
            "report_date": {
                "type": "date",
                "label": "Report Date",
                "required": True
            },
            "reporting_officer": {
                "type": "text",
                "label": "Reporting Officer and ID",
                "required": True,
                "value": "Sgt Steven Beltran 364"
            },
            "case_status": {
                "type": "select",
                "label": "Case Status",
                "options": ["Open", "Closed"],
                "required": True
            }
        },
        "complaint_info": {
            "complaint_type": {
                "type": "text",
                "label": "Complaint Type",
                "required": True,
                "value": ""
            },
            "location": {
                "type": "text",
                "label": "Location",
                "required": True,
                "value": ""
            },
            "county": {
                "type": "text",
                "label": "County of Occurrence",
                "required": True,
                "value": ""
            },
            "date_occurred": {
                "type": "date",
                "label": "Date Occurred",
                "required": True
            },
            "time_occurred": {
                "type": "text",
                "label": "Time Occurred",
                "required": False,
                "value": ""
            }
        },
        "subject_info": {
            "last_name": {
                "type": "text",
                "label": "Last Name",
                "required": True
            },
            "first_name": {
                "type": "text",
                "label": "First Name",
                "required": True
            },
            "dob": {
                "type": "date",
                "label": "Date of Birth",
                "required": False
            },
            "race": {
                "type": "select",
                "label": "Race",
                "options": ["W", "B", "H", "A", "O"],
                "required": False
            },
            "sex": {
                "type": "select",
                "label": "Sex",
                "options": ["M", "F"],
                "required": False
            },
            "height": {
                "type": "text",
                "label": "Height",
                "required": False,
                "value": ""
            },
            "weight": {
                "type": "number",
                "label": "Weight",
                "required": False,
                "value": 0
            },
            "hair": {
                "type": "text",
                "label": "Hair Color",
                "required": False
            },
            "eyes": {
                "type": "text",
                "label": "Eye Color",
                "required": False
            },
            "address": {
                "type": "text",
                "label": "Street Address",
                "required": False,
                "value": ""
            },
            "city": {
                "type": "text",
                "label": "City",
                "required": False,
                "value": ""
            },
            "state": {
                "type": "text",
                "label": "State",
                "required": False,
                "value": "IL"
            },
            "zip": {
                "type": "text",
                "label": "ZIP Code",
                "required": False,
                "value": ""
            },
            "phone": {
                "type": "text",
                "label": "Telephone",
                "required": False,
                "value": ""
            }
        },
        "charges": {
            "citation_code": {
                "type": "text",
                "label": "Citation Code",
                "required": True,
                "value": ""
            },
            "chapter_act": {
                "type": "text",
                "label": "Chapter/Act/Section",
                "required": False,
                "value": ""
            },
            "description": {
                "type": "text",
                "label": "Charge Description",
                "required": True,
                "value": ""
            }
        },
        "report_narrative": {
            "synopsis": {
                "type": "textarea",
                "label": "Synopsis (Brief Summary)",
                "required": True,
                "value": ""
            },
            "narrative": {
                "type": "textarea",
                "label": "Narrative (Detailed Report)",
                "required": True,
                "value": ""
            },
            "attachments": {
                "type": "text",
                "label": "Attachments/Evidence",
                "required": False,
                "value": ""
            }
        }
    }
