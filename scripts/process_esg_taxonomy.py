"""
Process ESG taxonomy CSV(s) and extract columns 1-7 into a clean JSON structure.
This creates a searchable taxonomy for mapping user concerns to ESG Field IDs.

Supports processing multiple CSV files (e.g., Environmental/Social and Governance separately)
and merging them into a single taxonomy.
"""

import csv
import json
from pathlib import Path
from typing import List


def process_single_csv(csv_path: str) -> List[dict]:
    """
    Extract metadata columns (1-7) from a single ESG CSV file.

    Args:
        csv_path: Path to the CSV file (e.g., "All ES Scores Fields.csv")

    Returns:
        List of field dictionaries
    """
    fields = []
    csv_name = Path(csv_path).stem  # e.g., "All ES Scores Fields"

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        # Skip the header/explanation rows (rows 1-9)
        for _ in range(9):
            next(reader)

        # Row 10 is the column headers - we'll skip it too
        headers = next(reader)

        # Process data rows
        for row in reader:
            if len(row) < 8:
                continue

            # Note: First column is empty, so actual columns are 1-7 (indices 1-7)
            pillar = row[1].strip() if len(row) > 1 and row[1] else ""
            issue = row[2].strip() if len(row) > 2 and row[2] else ""
            sub_issue = row[3].strip() if len(row) > 3 and row[3] else ""
            field_id = row[4].strip() if len(row) > 4 and row[4] else ""
            field_name = row[5].strip() if len(row) > 5 and row[5] else ""
            field_type = row[6].strip() if len(row) > 6 and row[6] else ""
            underlying_field_id = row[7].strip() if len(row) > 7 and row[7] else ""

            # Skip empty rows or rows without a field_id
            if not field_id or not field_name:
                continue

            # Create field entry
            field_entry = {
                "field_id": field_id,
                "field_name": field_name,
                "field_type": field_type,
                "pillar": pillar,
                "issue": issue,
                "sub_issue": sub_issue,
                "underlying_field_id": underlying_field_id,
                "source_file": csv_name,
                # Create searchable text combining all relevant fields
                "search_text": f"{field_name} {issue} {sub_issue} {pillar}".lower()
            }

            fields.append(field_entry)

    print(f"  ✓ Processed {len(fields)} fields from {csv_name}")
    return fields


def process_multiple_csvs(csv_paths: List[str], output_path: str):
    """
    Process multiple CSV files and merge them into a single taxonomy.

    Args:
        csv_paths: List of CSV file paths
        output_path: Path where the JSON taxonomy will be saved
    """
    all_fields = []

    print(f"Processing {len(csv_paths)} CSV files...\n")

    for csv_path in csv_paths:
        fields = process_single_csv(csv_path)
        all_fields.extend(fields)

    # Create the taxonomy structure
    taxonomy = {
        "version": "1.0",
        "source_files": [Path(p).name for p in csv_paths],
        "total_fields": len(all_fields),
        "fields": all_fields
    }

    # Save to JSON
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Total: {len(all_fields)} ESG fields")
    print(f"✓ Taxonomy saved to: {output_path}")

    # Print some stats
    pillars = set(f["pillar"] for f in all_fields if f["pillar"])
    issues = set(f["issue"] for f in all_fields if f["issue"])
    sources = set(f["source_file"] for f in all_fields)

    print(f"\nTaxonomy Stats:")
    print(f"  - Source Files: {', '.join(sources)}")
    print(f"  - Pillars: {len(pillars)} ({', '.join(sorted(pillars))})")
    print(f"  - Issues: {len(issues)}")
    print(f"  - Total Fields: {len(all_fields)}")

    return taxonomy


def process_esg_taxonomy(csv_path: str, output_path: str):
    """
    Legacy function for processing a single CSV.
    Maintained for backwards compatibility.

    Args:
        csv_path: Path to the CSV file
        output_path: Path where the JSON taxonomy will be saved
    """
    fields = process_single_csv(csv_path)

    # Create the taxonomy structure
    taxonomy = {
        "version": "1.0",
        "source": "All ES Scores Fields.csv",
        "total_fields": len(fields),
        "fields": fields
    }

    # Save to JSON
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)

    print(f"✓ Processed {len(fields)} ESG fields")
    print(f"✓ Taxonomy saved to: {output_path}")

    # Print some stats
    pillars = set(f["pillar"] for f in fields if f["pillar"])
    issues = set(f["issue"] for f in fields if f["issue"])

    print(f"\nTaxonomy Stats:")
    print(f"  - Pillars: {len(pillars)}")
    print(f"  - Issues: {len(issues)}")
    print(f"  - Total Fields: {len(fields)}")

    return taxonomy


if __name__ == "__main__":
    # Process both ES and G datasets
    csv_paths = [
        "data/All ES Scores Fields.csv",
        "data/All G Scores Fields.csv"
    ]
    output_path = "data/processed/esg_taxonomy.json"

    process_multiple_csvs(csv_paths, output_path)
