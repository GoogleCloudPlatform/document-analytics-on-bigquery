
import json

def deduplicate_files():
    files = [
        "/Users/ctimoteo/Projects/document-analytics-on-bigquery/sql/ClinicalTrialDenormalizedData-partaa.json",
        "/Users/ctimoteo/Projects/document-analytics-on-bigquery/sql/ClinicalTrialDenormalizedData-partab.json",
        "/Users/ctimoteo/Projects/document-analytics-on-bigquery/sql/ClinicalTrialDenormalizedData-partac.json",
        "/Users/ctimoteo/Projects/document-analytics-on-bigquery/sql/ClinicalTrialDenormalizedData-partad.json",
        "/Users/ctimoteo/Projects/document-analytics-on-bigquery/sql/ClinicalTrialDenormalizedData-partae.json",
        "/Users/ctimoteo/Projects/document-analytics-on-bigquery/sql/ClinicalTrialDenormalizedData-partaf.json"
    ]
    seen_posting_ids = set()

    for file_path in files:
        lines_to_keep = []
        with open(file_path, 'r') as f:
            for line in f:
                # Skip empty lines
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    posting_id = data.get("PostingID")
                    if posting_id not in seen_posting_ids:
                        lines_to_keep.append(line)
                        seen_posting_ids.add(posting_id)
                except json.JSONDecodeError as e:
                    print(f"Skipping line in {file_path} due to JSON decode error: {e}")
                    print(f"Problematic line: {line}")


        with open(file_path, 'w') as f:
            f.writelines(lines_to_keep)

if __name__ == "__main__":
    deduplicate_files()
