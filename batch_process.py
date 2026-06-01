"""
Standalone batch processing script for PDFs
Run this to process multiple PDFs without using the Streamlit interface

Usage:
    python batch_process.py --input /path/to/pdfs --output results.json
"""

import argparse
from pathlib import Path
from modules.pdf_processor import batch_process_pdfs, validate_pdf
from modules.database import create_report
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Batch process PDF field reports")

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Directory containing PDF files to process"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file for results (optional)"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate PDFs without processing"
    )

    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip saving to database (testing mode)"
    )

    args = parser.parse_args()

    input_dir = Path(args.input)

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"❌ Error: Directory not found: {args.input}")
        sys.exit(1)

    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ Error: No PDF files found in {args.input}")
        sys.exit(1)

    print(f"📋 Found {len(pdf_files)} PDF file(s)")

    if args.validate_only:
        print("\n🔍 Validating PDFs...")
        validate_pdfs(pdf_files)
    else:
        print("\n📤 Processing PDFs...")
        process_pdfs(pdf_files, args.output, args.skip_db)

    print("\n✅ Done!")


def validate_pdfs(pdf_files):
    """Validate PDF files"""

    for pdf_file in pdf_files:
        print(f"\n📄 {pdf_file.name}")

        from modules.pdf_processor import validate_pdf
        result = validate_pdf(str(pdf_file))

        if result["valid"]:
            print(f"  ✅ Valid PDF")
            print(f"     Pages: {result['num_pages']}")
            print(f"     Has text: {result['has_text']}")
            print(f"     Has tables: {result['has_tables']}")
        else:
            print(f"  ❌ Invalid PDF: {result['error']}")


def process_pdfs(pdf_files, output_json=None, skip_db=False):
    """Process PDF files"""

    results = []
    successful = 0
    failed = 0

    for idx, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_file.name}")

        try:
            from modules.pdf_processor import parse_pdf_report

            # Parse PDF
            report_data = parse_pdf_report(str(pdf_file))

            if report_data["extraction_status"] == "success":
                print(f"  ✅ Successfully extracted data")

                # Save to database if not skipping
                if not skip_db:
                    try:
                        db_report = create_report(
                            report_name=pdf_file.stem,
                            report_type="pdf_import",
                            field_data=report_data["extracted_data"],
                            source_file=pdf_file.name
                        )
                        print(f"  💾 Saved to database (ID: {db_report.id})")
                        report_data["database_id"] = db_report.id
                    except Exception as db_error:
                        print(f"  ⚠️  Failed to save to database: {db_error}")
                        report_data["database_error"] = str(db_error)

                successful += 1
            else:
                print(f"  ❌ Extraction error: {report_data.get('error_message', 'Unknown')}")
                failed += 1

            results.append(report_data)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
            results.append({
                "report_name": pdf_file.stem,
                "source_file": pdf_file.name,
                "extracted_data": {},
                "extraction_status": "error",
                "error_message": str(e)
            })

    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    print(f"Total files: {len(pdf_files)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")

    # Save results if requested
    if output_json:
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📝 Results saved to: {output_json}")


if __name__ == "__main__":
    main()
