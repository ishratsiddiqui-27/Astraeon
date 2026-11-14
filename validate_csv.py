import csv
import sys

def validate(filename="investigations.csv"):
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        print(f"Checking '{filename}': {len(headers)} columns expected.")
        errors = []
        for line_no, row in enumerate(reader, start=2):
            if len(row) != len(headers):
                errors.append(f"Line {line_no} ({row[0] if row else 'empty'}): has {len(row)} fields instead of {len(headers)}")
            elif row[8] != "microgravity":
                errors.append(f"Line {line_no} ({row[0]}): field 8 ('gravity') is '{row[8]}' instead of 'microgravity'")
            elif row[13] not in ["prevention", "detection", "suppression"]:
                errors.append(f"Line {line_no} ({row[0]}): field 13 ('topic') is '{row[13]}' which is not prevention/detection/suppression")

        if errors:
            print("Validation FAILED:")
            for err in errors:
                print(f" - {err}")
            sys.exit(1)
        else:
            print(f"ALL CHECKS PASSED: {line_no - 1} rows validated successfully!")

if __name__ == "__main__":
    validate()
