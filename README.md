# Field Reports System

A Python/Streamlit application for ingesting old PDF field reports and creating/managing new field reports in a database.

## Features

- **PDF Ingestion**: Upload and batch process PDF field reports
- **Dynamic Forms**: Create new field reports with dynamic, expandable fields
- **Database Storage**: Store all reports in MySQL database on omnis.com
- **Data Retrieval**: Search and filter reports by any field
- **Display**: View historical PDF data in the same format as new reports

## Tech Stack

- **Frontend**: Streamlit (hosted on Streamlit Cloud)
- **Backend**: Python
- **Database**: MySQL/MariaDB (on omnis.com)
- **PDF Processing**: pdfplumber
- **ORM**: SQLAlchemy

## Setup

### 1. Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root (see `.env.example`):

```bash
cp .env.example .env
```

Fill in your MySQL credentials and Streamlit Cloud settings.

### 3. Database Setup

Log into your omnis.com hosting control panel and:
1. Create a new MySQL database
2. Create a database user with full privileges
3. Note the host, username, password, and database name
4. Add to your `.env` file

### 4. Run Streamlit App

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Project Structure

```
field/
├── app.py                      # Main Streamlit app entry point
├── pages/
│   ├── batch_upload.py        # Batch PDF upload interface
│   ├── create_report.py       # New report form creation
│   └── view_reports.py        # Search and display reports
├── modules/
│   ├── pdf_processor.py       # PDF extraction and parsing
│   ├── database.py            # MySQL database operations
│   └── forms.py               # Dynamic form generation
├── batch_process.py           # Standalone batch processing script
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── .gitignore
```

## Workflow

### Ingesting Old Reports

1. Navigate to "Batch Upload" page
2. Upload PDF field reports
3. System extracts data and stores in database
4. Historical data is queryable and displayable

### Creating New Reports

1. Navigate to "Create Report" page
2. Fill in dynamic form fields
3. Submit to database
4. Report appears in searchable list

### Viewing Reports

1. Navigate to "View Reports" page
2. Search by any field value
3. View report details (whether from PDF or newly created)

## SSO Authentication

To be added in Phase 2. Will integrate with:
- Google OAuth
- Microsoft Azure AD
- Or other enterprise SSO providers

## Database Schema

The system uses a flexible schema to handle various field types:
- Text fields
- Numeric fields
- Date fields
- Dynamic arrays/expandable sections
- Images (from PDFs)

## Development Notes

- PDF templates are consistent with dynamic fields based on data entry
- Batch uploads preferred but manual upload also supported
- Database is self-hosted on omnis.com for flexibility and control
- Streamlit Cloud handles the frontend

## Future Enhancements

- [ ] SSO authentication (Google/Azure)
- [ ] Advanced filtering and reporting
- [ ] PDF export of new reports
- [ ] Report versioning
- [ ] Audit logging
- [ ] Role-based access control

## Support

For issues or feature requests, contact: steven.beltran@brincdrones.com
