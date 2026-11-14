import csv
import os
import sys

def validate(filename=None):
    if filename is None:
        if os.path.exists("data/investigations.csv"):
            filename = "data/investigations.csv"
        else:
            filename = "investigations.csv"

    if not os.path.exists(filename):
        print(f"Error: file '{filename}' not found.")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        print(f"Checking '{filename}': {len(headers)} columns expected.")
        errors = []
        for line_no, row in enumerate(reader, start=2):
            if len(row) != len(headers):
                errors.append(f"Line {line_no} ({row[0] if row else 'empty'}): has {len(row)} fields instead of {len(headers)}")
            elif row[8] not in ["microgravity", "normal gravity"]:
                errors.append(f"Line {line_no} ({row[0]}): field 8 ('gravity') is '{row[8]}' instead of microgravity/normal gravity")
            elif row[13] not in ["prevention", "detection", "suppression"]:
                errors.append(f"Line {line_no} ({row[0]}): field 13 ('topic') is '{row[13]}' which is not prevention/detection/suppression")
            elif row[17] not in ["flight", "modeling", "ground"]:
                errors.append(f"Line {line_no} ({row[0]}): field 17 ('study_type') is '{row[17]}' which is not flight/modeling/ground")

        if errors:
            print("Validation FAILED:")
            for err in errors:
                print(f" - {err}")
            sys.exit(1)
        else:
            print(f"ALL CHECKS PASSED: {line_no - 1} rows validated successfully!")

if __name__ == "__main__":
    validate()
