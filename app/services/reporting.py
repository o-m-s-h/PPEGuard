import json
import csv
import os


VIOLATION_SEVERITY = {
    "NO-Hardhat": "high",
    "NO-Safety Vest": "medium",
    "NO-Mask": "low"
}


def is_violation(class_name):
    return class_name in VIOLATION_SEVERITY


def get_severity(class_name):
    return VIOLATION_SEVERITY.get(
        class_name,
        "unknown"
    )


def save_json_report(data, filename):

    os.makedirs(
        "outputs/reports/json",
        exist_ok=True
    )

    path = os.path.join(
        "outputs/reports/json",
        filename
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

    return path


def save_csv_report(rows, filename):

    os.makedirs(
        "outputs/reports/csv",
        exist_ok=True
    )

    path = os.path.join(
        "outputs/reports/csv",
        filename
    )

    if not rows:

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "type",
                "confidence",
                "severity",
                "timestamp"
            ])

        return path


    fieldnames = rows[0].keys()


    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)


    return path